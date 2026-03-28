from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

JWT_ALGORITHM = "HS256"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Password Hashing ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

# --- JWT ---
def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=30), "type": "access"}
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
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Models ---
class RegisterInput(BaseModel):
    username: str
    email: str
    password: str

class LoginInput(BaseModel):
    email: str
    password: str

class FriendRequestInput(BaseModel):
    username: str  # without @ prefix

class MessageInput(BaseModel):
    receiver_id: str
    content: str

# --- Auth Endpoints ---
@api_router.post("/auth/register")
async def register(input_data: RegisterInput, response: Response):
    email = input_data.email.strip().lower()
    username = input_data.username.strip().lower()

    if len(input_data.password) < 6:
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
        "password_hash": hash_password(input_data.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "friends": [],
        "online": False
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

    return {"id": user_id, "username": username, "email": email, "token": access_token}

@api_router.post("/auth/login")
async def login(input_data: LoginInput, response: Response, request: Request):
    email = input_data.email.strip().lower()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"

    # Brute force check
    attempt = await db.login_attempts.find_one({"identifier": identifier}, {"_id": 0})
    if attempt and attempt.get("count", 0) >= 5:
        lockout_time = attempt.get("last_attempt")
        if lockout_time:
            if isinstance(lockout_time, str):
                lockout_time = datetime.fromisoformat(lockout_time)
            if datetime.now(timezone.utc) - lockout_time < timedelta(minutes=15):
                raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")

    user = await db.users.find_one({"email": email})
    if not user:
        await _record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(input_data.password, user["password_hash"]):
        await _record_failed_attempt(identifier)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Clear failed attempts
    await db.login_attempts.delete_one({"identifier": identifier})

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")

    return {"id": user_id, "username": user["username"], "email": email, "token": access_token}

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
        access_token = create_access_token(str(user["_id"]), user["email"])
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=1800, path="/")
        return {"message": "Token refreshed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

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

    # Check if already friends
    if target_id in user.get("friends", []):
        raise HTTPException(status_code=400, detail="Already friends")

    # Check existing request
    existing = await db.friend_requests.find_one({
        "$or": [
            {"from_id": user["_id"], "to_id": target_id},
            {"from_id": target_id, "to_id": user["_id"]}
        ],
        "status": "pending"
    }, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Friend request already exists")

    await db.friend_requests.insert_one({
        "from_id": user["_id"],
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
        {"to_id": user["_id"], "status": "pending"}, {"_id": 0}
    ).to_list(100)

    # Convert ObjectId fields
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
        {"from_id": user["_id"], "status": "pending"}, {"_id": 0}
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
        "to_id": user["_id"],
        "status": "pending"
    })
    if not req:
        raise HTTPException(status_code=404, detail="Friend request not found")

    from_id = req["from_id"]
    if isinstance(from_id, ObjectId):
        from_id = str(from_id)

    # Add each other as friends
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$addToSet": {"friends": from_id}})
    await db.users.update_one({"_id": ObjectId(from_id)}, {"$addToSet": {"friends": user["_id"]}})

    # Update request status
    await db.friend_requests.update_one({"_id": req["_id"]}, {"$set": {"status": "accepted"}})
    return {"message": f"You are now friends with @{from_username}"}

@api_router.post("/friends/reject")
async def reject_friend_request(input_data: FriendRequestInput, request: Request):
    user = await get_current_user(request)
    from_username = input_data.username.strip().lower().lstrip("@")

    result = await db.friend_requests.update_one(
        {"from_username": from_username, "to_id": user["_id"], "status": "pending"},
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
            friend = await db.users.find_one({"_id": ObjectId(fid)}, {"password_hash": 0})
            if friend:
                friend["_id"] = str(friend["_id"])
                friends.append({"id": friend["_id"], "username": friend["username"], "email": friend["email"], "online": friend.get("online", False)})
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
        {"username": {"$regex": f"^{query}", "$options": "i"}, "_id": {"$ne": ObjectId(user["_id"])}},
        {"password_hash": 0}
    ).to_list(10)
    results = []
    for u in users:
        u["_id"] = str(u["_id"])
        results.append({"id": u["_id"], "username": u["username"]})
    return results

# --- Message Endpoints ---
@api_router.post("/messages")
async def send_message(input_data: MessageInput, request: Request):
    user = await get_current_user(request)

    # Verify they are friends
    if input_data.receiver_id not in user.get("friends", []):
        raise HTTPException(status_code=403, detail="You can only message friends")

    msg_doc = {
        "sender_id": user["_id"],
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
            {"sender_id": user["_id"], "receiver_id": friend_id},
            {"sender_id": friend_id, "receiver_id": user["_id"]}
        ]},
        {"_id": 0}
    ).sort("created_at", 1).to_list(200)
    return messages

# --- Startup ---
@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.login_attempts.create_index("identifier")

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "username": "admin",
            "email": admin_email,
            "password_hash": hash_password(admin_password),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "friends": [],
            "online": False,
            "role": "admin"
        })
        logger.info("Admin user seeded")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})

    # Write test credentials
    os.makedirs("/app/memory", exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write(f"## Admin\n- Email: {admin_email}\n- Password: {admin_password}\n- Role: admin\n\n")
        f.write("## Auth Endpoints\n- POST /api/auth/register\n- POST /api/auth/login\n- POST /api/auth/logout\n- GET /api/auth/me\n- POST /api/auth/refresh\n\n")
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
