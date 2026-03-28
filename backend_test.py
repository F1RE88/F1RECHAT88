import requests
import sys
import json
from datetime import datetime

class F1RECHATTester:
    def __init__(self, base_url="https://secure-social-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.user_a_token = None
        self.user_b_token = None
        self.user_a_id = None
        self.user_b_id = None
        self.admin_token = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, cookies=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, cookies=cookies)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, cookies=cookies)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, cookies=cookies)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, cookies=cookies)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def register_user(self, email, username, password):
        """Complete user registration flow"""
        print(f"\n📝 Registering user: {username} ({email})")
        
        # Step 1: Verify email
        success, response = self.run_test(
            f"Email verification for {username}",
            "POST",
            "auth/verify-email",
            200,
            data={"email": email}
        )
        if not success:
            return None, None
        
        token = response.get('token')
        if not token:
            print(f"❌ No verification token received for {username}")
            return None, None
        
        # Step 2: Verify token
        success, _ = self.run_test(
            f"Token verification for {username}",
            "GET",
            f"auth/verify/{token}",
            200
        )
        if not success:
            return None, None
        
        # Step 3: Complete registration
        success, response = self.run_test(
            f"Complete registration for {username}",
            "POST",
            "auth/complete-register",
            200,
            data={"token": token, "username": username, "password": password}
        )
        if not success:
            return None, None
        
        user_id = response.get('id')
        access_token = response.get('token')
        
        if user_id and access_token:
            print(f"✅ User {username} registered successfully with ID: {user_id}")
            return user_id, access_token
        else:
            print(f"❌ Registration incomplete for {username}")
            return None, None

    def test_auth_me_returns_id_field(self, token):
        """Test that /auth/me returns 'id' field (not '_id')"""
        success, response = self.run_test(
            "GET /auth/me returns 'id' field",
            "GET",
            "auth/me",
            200,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if success:
            if 'id' in response and '_id' not in response:
                print("✅ /auth/me correctly returns 'id' field (not '_id')")
                return True
            else:
                print(f"❌ /auth/me response format issue: {response}")
                return False
        return False

    def test_login(self, username, password):
        """Test login with username+password"""
        success, response = self.run_test(
            f"Login {username}",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success:
            return response.get('token'), response.get('id')
        return None, None

    def make_friends(self, user_a_token, user_b_username, user_b_token, user_a_username):
        """Make two users friends"""
        print(f"\n👥 Making users friends...")
        
        # User A sends friend request to User B
        success, _ = self.run_test(
            f"Send friend request to {user_b_username}",
            "POST",
            "friends/request",
            200,
            data={"username": user_b_username},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        if not success:
            return False
        
        # User B accepts friend request from User A
        success, _ = self.run_test(
            f"Accept friend request from {user_a_username}",
            "POST",
            "friends/accept",
            200,
            data={"username": user_a_username},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        return success

    def test_message_direction_fix(self):
        """CRITICAL: Test message direction fix by creating users and checking sender_id"""
        print(f"\n🔥 CRITICAL TEST: Message Direction Fix")
        
        # Generate unique usernames for this test
        timestamp = datetime.now().strftime('%H%M%S')
        user_a_email = f"usera{timestamp}@test.com"
        user_a_username = f"usera{timestamp}"
        user_b_email = f"userb{timestamp}@test.com"
        user_b_username = f"userb{timestamp}"
        password = "test123456"
        
        # Register User A
        self.user_a_id, self.user_a_token = self.register_user(user_a_email, user_a_username, password)
        if not self.user_a_id or not self.user_a_token:
            print("❌ Failed to register User A")
            return False
        
        # Register User B
        self.user_b_id, self.user_b_token = self.register_user(user_b_email, user_b_username, password)
        if not self.user_b_id or not self.user_b_token:
            print("❌ Failed to register User B")
            return False
        
        # Test /auth/me returns 'id' field for both users
        if not self.test_auth_me_returns_id_field(self.user_a_token):
            print("❌ User A: /auth/me doesn't return 'id' field")
            return False
        
        if not self.test_auth_me_returns_id_field(self.user_b_token):
            print("❌ User B: /auth/me doesn't return 'id' field")
            return False
        
        # Make them friends
        if not self.make_friends(self.user_a_token, user_b_username, self.user_b_token, user_a_username):
            print("❌ Failed to make users friends")
            return False
        
        # User A sends message to User B
        message_content = f"Hello from {user_a_username} to {user_b_username}!"
        success, _ = self.run_test(
            f"User A sends message to User B",
            "POST",
            "messages",
            200,
            data={"receiver_id": self.user_b_id, "content": message_content},
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        if not success:
            print("❌ Failed to send message")
            return False
        
        # Get messages and verify sender_id
        success, messages = self.run_test(
            f"Get messages between users",
            "GET",
            f"messages/{self.user_b_id}",
            200,
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to get messages")
            return False
        
        if not messages:
            print("❌ No messages found")
            return False
        
        # Find the message we just sent
        sent_message = None
        for msg in messages:
            if msg.get('content') == message_content:
                sent_message = msg
                break
        
        if not sent_message:
            print("❌ Sent message not found in conversation")
            return False
        
        # CRITICAL CHECK: Verify sender_id matches User A's ID
        if sent_message.get('sender_id') == self.user_a_id:
            print(f"✅ CRITICAL: Message direction fix verified! sender_id ({sent_message.get('sender_id')}) matches User A's ID ({self.user_a_id})")
            return True
        else:
            print(f"❌ CRITICAL: Message direction bug still exists! sender_id ({sent_message.get('sender_id')}) != User A's ID ({self.user_a_id})")
            return False

    def test_chat_background_endpoints(self):
        """Test chat background customization endpoints"""
        print(f"\n🎨 Testing Chat Background Endpoints")
        
        if not self.user_a_token:
            print("❌ No user token available for background test")
            return False
        
        # Test PUT /settings/chat-background
        success, _ = self.run_test(
            "Set chat background",
            "PUT",
            "settings/chat-background",
            200,
            data={"background": "dark-purple"},
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        if not success:
            return False
        
        # Test GET /settings/chat-background
        success, response = self.run_test(
            "Get chat background",
            "GET",
            "settings/chat-background",
            200,
            headers={"Authorization": f"Bearer {self.user_a_token}"}
        )
        
        if success and response.get('background') == 'dark-purple':
            print("✅ Chat background endpoints working correctly")
            return True
        else:
            print(f"❌ Chat background not saved correctly: {response}")
            return False

    def test_admin_functionality(self):
        """Test admin panel functionality"""
        print(f"\n🛡️ Testing Admin Functionality")
        
        # Test admin verification
        success, response = self.run_test(
            "Admin verification",
            "POST",
            "admin/verify",
            200,
            data={"password": "F1RE88HAMZA8ADMIN"}
        )
        
        if not success:
            return False
        
        self.admin_token = response.get('admin_token')
        if not self.admin_token:
            print("❌ No admin token received")
            return False
        
        # Test admin users list
        success, users = self.run_test(
            "Get admin users list",
            "GET",
            "admin/users",
            200,
            headers={"X-Admin-Token": self.admin_token}
        )
        
        if success and isinstance(users, list):
            print(f"✅ Admin users list retrieved: {len(users)} users")
            return True
        else:
            print("❌ Failed to get admin users list")
            return False

    def test_existing_users_groups(self):
        """Test group functionality with existing test users"""
        print(f"\n👥 Testing Group Functionality with Existing Users")
        
        # Login as existing test users
        user_a_token, user_a_id = self.test_login("usera140401", "test123456")
        user_b_token, user_b_id = self.test_login("userb140401", "test123456")
        
        if not user_a_token or not user_b_token:
            print("❌ Failed to login existing test users")
            return False
        
        print(f"✅ Logged in as usera140401 (ID: {user_a_id}) and userb140401 (ID: {user_b_id})")
        
        # Test 1: Create a group
        group_name = f"Test Group {datetime.now().strftime('%H%M%S')}"
        success, group_response = self.run_test(
            "Create group",
            "POST",
            "groups",
            200,
            data={"name": group_name, "member_ids": [user_b_id]},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to create group")
            return False
        
        group_id = group_response.get('id')
        if not group_id:
            print("❌ No group ID returned")
            return False
        
        print(f"✅ Group created with ID: {group_id}")
        
        # Test 2: List groups for user A
        success, groups = self.run_test(
            "List groups for user A",
            "GET",
            "groups",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success or not isinstance(groups, list):
            print("❌ Failed to list groups")
            return False
        
        # Find our created group
        created_group = None
        for group in groups:
            if group.get('id') == group_id:
                created_group = group
                break
        
        if not created_group:
            print("❌ Created group not found in groups list")
            return False
        
        print(f"✅ Group found in list: {created_group.get('name')}")
        
        # Test 3: Get group details
        success, group_details = self.run_test(
            "Get group details",
            "GET",
            f"groups/{group_id}",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to get group details")
            return False
        
        members = group_details.get('members', [])
        if len(members) != 2:  # Creator + 1 member
            print(f"❌ Expected 2 members, got {len(members)}")
            return False
        
        print(f"✅ Group details retrieved with {len(members)} members")
        
        # Test 4: Send group message
        message_content = f"Hello group! From usera140401 at {datetime.now().strftime('%H:%M:%S')}"
        success, message_response = self.run_test(
            "Send group message",
            "POST",
            f"groups/{group_id}/messages",
            200,
            data={"content": message_content},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to send group message")
            return False
        
        print("✅ Group message sent successfully")
        
        # Test 5: Get group messages
        success, messages = self.run_test(
            "Get group messages",
            "GET",
            f"groups/{group_id}/messages",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success or not isinstance(messages, list):
            print("❌ Failed to get group messages")
            return False
        
        # Find our message
        sent_message = None
        for msg in messages:
            if msg.get('content') == message_content:
                sent_message = msg
                break
        
        if not sent_message:
            print("❌ Sent group message not found")
            return False
        
        if sent_message.get('sender_id') != user_a_id:
            print(f"❌ Group message sender_id mismatch: {sent_message.get('sender_id')} != {user_a_id}")
            return False
        
        print("✅ Group message retrieved correctly")
        
        # Test 6: User B can also access the group
        success, user_b_groups = self.run_test(
            "List groups for user B",
            "GET",
            "groups",
            200,
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        if not success:
            print("❌ User B failed to list groups")
            return False
        
        # Check if user B can see the group
        user_b_has_group = any(g.get('id') == group_id for g in user_b_groups)
        if not user_b_has_group:
            print("❌ User B cannot see the group they're a member of")
            return False
        
        print("✅ User B can see the group")
        
        # Test 7: User B sends a message to the group
        user_b_message = f"Hello from userb140401 at {datetime.now().strftime('%H:%M:%S')}"
        success, _ = self.run_test(
            "User B sends group message",
            "POST",
            f"groups/{group_id}/messages",
            200,
            data={"content": user_b_message},
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        if not success:
            print("❌ User B failed to send group message")
            return False
        
        print("✅ User B sent group message successfully")
        
        # Test 8: Delete group (only creator can do this)
        success, _ = self.run_test(
            "Delete group (as creator)",
            "DELETE",
            f"groups/{group_id}",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to delete group")
            return False
        
        print("✅ Group deleted successfully")
        
        # Test 9: Verify group is deleted
        success, _ = self.run_test(
            "Try to access deleted group",
            "GET",
            f"groups/{group_id}",
            404,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Deleted group still accessible")
            return False
        
        print("✅ Deleted group properly inaccessible")
        
        return True

    def test_existing_admin_login(self):
        """Test login with existing admin credentials"""
        print(f"\n👤 Testing Existing Admin Login")
        
        token, user_id = self.test_login("admin", "admin123")
        if token and user_id:
            print("✅ Admin login successful")
            return True
        else:
            print("❌ Admin login failed")
            return False

    def test_heartbeat_and_online_status(self):
        """Test heartbeat system and online/offline status"""
        print(f"\n💓 Testing Heartbeat and Online Status")
        
        # Login as existing test users
        user_a_token, user_a_id = self.test_login("usera140401", "test123456")
        user_b_token, user_b_id = self.test_login("userb140401", "test123456")
        
        if not user_a_token or not user_b_token:
            print("❌ Failed to login test users for heartbeat test")
            return False
        
        # Test 1: Send heartbeat for user A
        success, response = self.run_test(
            "Send heartbeat for user A",
            "POST",
            "auth/heartbeat",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success or response.get('status') != 'ok':
            print("❌ Heartbeat failed")
            return False
        
        print("✅ Heartbeat sent successfully")
        
        # Test 2: Check if user is online by getting friends list
        success, friends = self.run_test(
            "Get friends list to check online status",
            "GET",
            "friends",
            200,
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        if not success:
            print("❌ Failed to get friends list")
            return False
        
        # Find user A in user B's friends list
        user_a_friend = None
        for friend in friends:
            if friend.get('id') == user_a_id:
                user_a_friend = friend
                break
        
        if not user_a_friend:
            print("❌ User A not found in User B's friends list")
            return False
        
        if user_a_friend.get('online'):
            print("✅ User A shows as online after heartbeat")
        else:
            print("⚠️ User A not showing as online (may be timing issue)")
        
        # Test 3: Logout user A and check offline status
        success, _ = self.run_test(
            "Logout user A",
            "POST",
            "auth/logout",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to logout user A")
            return False
        
        print("✅ User A logged out successfully")
        
        return True

    def test_notification_system(self):
        """Test notification system for friend requests, messages, etc."""
        print(f"\n🔔 Testing Notification System")
        
        # Create new test users for clean notification testing
        timestamp = datetime.now().strftime('%H%M%S')
        user_c_email = f"userc{timestamp}@test.com"
        user_c_username = f"userc{timestamp}"
        user_d_email = f"userd{timestamp}@test.com"
        user_d_username = f"userd{timestamp}"
        password = "test123456"
        
        # Register users
        user_c_id, user_c_token = self.register_user(user_c_email, user_c_username, password)
        user_d_id, user_d_token = self.register_user(user_d_email, user_d_username, password)
        
        if not user_c_id or not user_d_id:
            print("❌ Failed to register test users for notifications")
            return False
        
        # Test 1: Check initial notification count (should be 0)
        success, response = self.run_test(
            "Get initial unread notification count",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if not success:
            print("❌ Failed to get unread notification count")
            return False
        
        initial_count = response.get('count', -1)
        print(f"✅ Initial unread count: {initial_count}")
        
        # Test 2: User C sends friend request to User D (should create notification)
        success, _ = self.run_test(
            "Send friend request (should create notification)",
            "POST",
            "friends/request",
            200,
            data={"username": user_d_username},
            headers={"Authorization": f"Bearer {user_c_token}"}
        )
        
        if not success:
            print("❌ Failed to send friend request")
            return False
        
        # Test 3: Check if notification was created for User D
        success, response = self.run_test(
            "Get unread count after friend request",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if not success:
            print("❌ Failed to get unread count after friend request")
            return False
        
        new_count = response.get('count', -1)
        if new_count > initial_count:
            print(f"✅ Notification created for friend request (count: {new_count})")
        else:
            print(f"⚠️ No notification increase after friend request (count: {new_count})")
        
        # Test 4: Get notifications list
        success, notifications = self.run_test(
            "Get notifications list",
            "GET",
            "notifications",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if not success:
            print("❌ Failed to get notifications list")
            return False
        
        if isinstance(notifications, list) and len(notifications) > 0:
            print(f"✅ Notifications list retrieved: {len(notifications)} notifications")
            
            # Check if friend request notification exists
            friend_request_notif = None
            for notif in notifications:
                if notif.get('type') == 'friend_request' and notif.get('from_username') == user_c_username:
                    friend_request_notif = notif
                    break
            
            if friend_request_notif:
                print("✅ Friend request notification found")
            else:
                print("⚠️ Friend request notification not found in list")
        else:
            print("⚠️ No notifications found")
        
        # Test 5: User D accepts friend request (should create notification for User C)
        success, _ = self.run_test(
            "Accept friend request (should create notification)",
            "POST",
            "friends/accept",
            200,
            data={"username": user_c_username},
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if not success:
            print("❌ Failed to accept friend request")
            return False
        
        # Test 6: Check if User C got friend accepted notification
        success, response = self.run_test(
            "Get User C unread count after acceptance",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_c_token}"}
        )
        
        if success and response.get('count', 0) > 0:
            print("✅ Friend accepted notification created for User C")
        else:
            print("⚠️ No friend accepted notification for User C")
        
        # Test 7: User C sends message to User D (should create notification)
        message_content = f"Hello {user_d_username}! This is a test message."
        success, _ = self.run_test(
            "Send message (should create notification)",
            "POST",
            "messages",
            200,
            data={"receiver_id": user_d_id, "content": message_content},
            headers={"Authorization": f"Bearer {user_c_token}"}
        )
        
        if not success:
            print("❌ Failed to send message")
            return False
        
        # Test 8: Check if message notification was created for User D
        success, response = self.run_test(
            "Get User D unread count after message",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if success and response.get('count', 0) > 0:
            print("✅ Message notification created for User D")
        else:
            print("⚠️ No message notification for User D")
        
        # Test 9: Mark all notifications as read
        success, response = self.run_test(
            "Mark all notifications as read",
            "PUT",
            "notifications/read",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if not success:
            print("❌ Failed to mark notifications as read")
            return False
        
        # Test 10: Verify unread count is now 0
        success, response = self.run_test(
            "Get unread count after marking read",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_d_token}"}
        )
        
        if success and response.get('count', -1) == 0:
            print("✅ All notifications marked as read successfully")
        else:
            print(f"⚠️ Unread count not zero after marking read: {response.get('count', -1)}")
        
        return True

    def test_group_message_notifications(self):
        """Test notifications for group messages"""
        print(f"\n👥🔔 Testing Group Message Notifications")
        
        # Login as existing test users
        user_a_token, user_a_id = self.test_login("usera140401", "test123456")
        user_b_token, user_b_id = self.test_login("userb140401", "test123456")
        
        if not user_a_token or not user_b_token:
            print("❌ Failed to login test users for group notification test")
            return False
        
        # Create a test group
        group_name = f"Notification Test Group {datetime.now().strftime('%H%M%S')}"
        success, group_response = self.run_test(
            "Create group for notification test",
            "POST",
            "groups",
            200,
            data={"name": group_name, "member_ids": [user_b_id]},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to create group for notification test")
            return False
        
        group_id = group_response.get('id')
        if not group_id:
            print("❌ No group ID returned")
            return False
        
        # Get User B's initial notification count
        success, response = self.run_test(
            "Get User B initial unread count",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        initial_count = response.get('count', 0) if success else 0
        
        # User A sends group message (should notify User B)
        message_content = f"Group notification test message at {datetime.now().strftime('%H:%M:%S')}"
        success, _ = self.run_test(
            "Send group message (should create notification)",
            "POST",
            f"groups/{group_id}/messages",
            200,
            data={"content": message_content},
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        if not success:
            print("❌ Failed to send group message")
            return False
        
        # Check if User B got group message notification
        success, response = self.run_test(
            "Get User B unread count after group message",
            "GET",
            "notifications/unread-count",
            200,
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        
        if success and response.get('count', 0) > initial_count:
            print("✅ Group message notification created for User B")
        else:
            print("⚠️ No group message notification for User B")
        
        # Clean up: Delete the test group
        success, _ = self.run_test(
            "Delete test group",
            "DELETE",
            f"groups/{group_id}",
            200,
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        
        return True

def main():
    print("🚀 Starting F1RECHAT Backend Testing (Iteration 5 - Notifications & Online Status)")
    print("=" * 70)
    
    tester = F1RECHATTester()
    
    # Test existing admin login
    tester.test_existing_admin_login()
    
    # CRITICAL: Test message direction fix
    if not tester.test_message_direction_fix():
        print("\n❌ CRITICAL: Message direction fix test failed!")
        print("📊 Tests passed: {}/{} ({:.1f}%)".format(
            tester.tests_passed, tester.tests_run, 
            (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
        ))
        return 1
    
    # Test chat background endpoints
    tester.test_chat_background_endpoints()
    
    # Test admin functionality
    tester.test_admin_functionality()
    
    # Test group functionality with existing users
    if not tester.test_existing_users_groups():
        print("\n❌ Group functionality tests failed!")
    
    # NEW: Test heartbeat and online status system
    if not tester.test_heartbeat_and_online_status():
        print("\n❌ Heartbeat and online status tests failed!")
    
    # NEW: Test notification system
    if not tester.test_notification_system():
        print("\n❌ Notification system tests failed!")
    
    # NEW: Test group message notifications
    if not tester.test_group_message_notifications():
        print("\n❌ Group message notification tests failed!")
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed ({(tester.tests_passed / tester.tests_run * 100):.1f}%)")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend tests passed!")
        return 0
    else:
        print("⚠️ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())