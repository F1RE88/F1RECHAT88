#!/usr/bin/env python3
"""
Backend API Testing for Social Platform
Tests all auth, friends, and messaging endpoints
"""

import requests
import sys
import json
from datetime import datetime

class SocialPlatformTester:
    def __init__(self, base_url="https://secure-social-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None
        self.test_users = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, cookies=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login with credentials from test_credentials.md"""
        self.log("=== Testing Admin Login ===")
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@example.com", "password": "admin123"}
        )
        if success:
            self.current_user = response
            self.log(f"Admin logged in: {response.get('username', 'N/A')}")
        return success

    def test_user_registration(self):
        """Test user registration with testuser2 as specified"""
        self.log("=== Testing User Registration ===")
        
        # Test registration with testuser2
        success, response = self.run_test(
            "Register testuser2",
            "POST", 
            "auth/register",
            200,
            data={
                "username": "testuser2",
                "email": "testuser2@test.com", 
                "password": "test123456"
            }
        )
        if success:
            self.test_users.append(response)
            self.current_user = response
            self.log(f"User registered: {response.get('username', 'N/A')}")
        
        return success

    def test_user_login(self):
        """Test user login with registered credentials"""
        self.log("=== Testing User Login ===")
        success, response = self.run_test(
            "Login testuser2",
            "POST",
            "auth/login", 
            200,
            data={"email": "testuser2@test.com", "password": "test123456"}
        )
        if success:
            self.current_user = response
            self.log(f"User logged in: {response.get('username', 'N/A')}")
        return success

    def test_get_current_user(self):
        """Test GET /api/auth/me endpoint"""
        self.log("=== Testing Get Current User ===")
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        if success:
            self.log(f"Current user: {response.get('username', 'N/A')} ({response.get('email', 'N/A')})")
        return success

    def test_logout(self):
        """Test logout endpoint"""
        self.log("=== Testing Logout ===")
        success, response = self.run_test(
            "Logout",
            "POST",
            "auth/logout",
            200
        )
        if success:
            self.current_user = None
            self.log("User logged out successfully")
        return success

    def test_friend_search(self):
        """Test friend search functionality"""
        self.log("=== Testing Friend Search ===")
        
        # Search for 'test' users
        success, response = self.run_test(
            "Search Users (test)",
            "GET",
            "friends/search?q=test",
            200
        )
        if success:
            self.log(f"Found {len(response)} users matching 'test'")
            for user in response:
                self.log(f"  - {user.get('username', 'N/A')}")
        
        return success

    def test_send_friend_request(self):
        """Test sending friend request to testuser1"""
        self.log("=== Testing Send Friend Request ===")
        
        # First, let's try to send a request to admin (since we know admin exists)
        success, response = self.run_test(
            "Send Friend Request to admin",
            "POST",
            "friends/request",
            200,
            data={"username": "admin"}
        )
        if success:
            self.log(f"Friend request sent: {response.get('message', 'N/A')}")
        
        return success

    def test_get_friend_requests(self):
        """Test getting friend requests"""
        self.log("=== Testing Get Friend Requests ===")
        success, response = self.run_test(
            "Get Friend Requests",
            "GET",
            "friends/requests",
            200
        )
        if success:
            self.log(f"Found {len(response)} friend requests")
        return success

    def test_get_friends(self):
        """Test getting friends list"""
        self.log("=== Testing Get Friends ===")
        success, response = self.run_test(
            "Get Friends",
            "GET", 
            "friends",
            200
        )
        if success:
            self.log(f"Found {len(response)} friends")
        return success

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        self.log("=== Testing Invalid Login ===")
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={"email": "invalid@test.com", "password": "wrongpassword"}
        )
        return success

    def test_duplicate_registration(self):
        """Test registration with existing email"""
        self.log("=== Testing Duplicate Registration ===")
        success, response = self.run_test(
            "Duplicate Registration",
            "POST",
            "auth/register",
            400,
            data={
                "username": "testuser3",
                "email": "testuser2@test.com",  # Same email as testuser2
                "password": "test123456"
            }
        )
        return success

    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.log("🚀 Starting Social Platform Backend Tests")
        self.log(f"Testing against: {self.base_url}")
        
        # Test sequence
        tests = [
            ("Admin Login", self.test_admin_login),
            ("User Registration", self.test_user_registration),
            ("Get Current User (after register)", self.test_get_current_user),
            ("Logout", self.test_logout),
            ("User Login", self.test_user_login),
            ("Get Current User (after login)", self.test_get_current_user),
            ("Friend Search", self.test_friend_search),
            ("Send Friend Request", self.test_send_friend_request),
            ("Get Friend Requests", self.test_get_friend_requests),
            ("Get Friends", self.test_get_friends),
            ("Invalid Login", self.test_invalid_login),
            ("Duplicate Registration", self.test_duplicate_registration),
        ]
        
        failed_tests = []
        for test_name, test_func in tests:
            try:
                if not test_func():
                    failed_tests.append(test_name)
            except Exception as e:
                self.log(f"❌ {test_name} - Exception: {str(e)}")
                failed_tests.append(test_name)
        
        # Results
        self.log("\n" + "="*50)
        self.log("📊 TEST RESULTS")
        self.log("="*50)
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Tests Failed: {self.tests_run - self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if failed_tests:
            self.log(f"\n❌ Failed Tests: {', '.join(failed_tests)}")
        else:
            self.log("\n✅ All tests passed!")
        
        return self.tests_passed == self.tests_run

def main():
    tester = SocialPlatformTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())