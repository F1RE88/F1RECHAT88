import requests
import sys
import json
from datetime import datetime

class F1RECHATAPITester:
    def __init__(self, base_url="https://secure-social-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            response_data = {}
            try:
                response_data = response.json()
            except:
                pass

            if success:
                self.log_test(name, True)
            else:
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}")

            return success, response_data, response.status_code

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}, 0

    def test_email_verification_flow(self):
        """Test the multi-step registration: email verification"""
        print("\n🔍 Testing Email Verification Flow...")
        
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        
        # Step 1: Send email verification
        success, response, status = self.run_test(
            "Email verification request",
            "POST",
            "auth/verify-email",
            200,
            {"email": test_email}
        )
        
        if not success:
            return None, None
            
        # Check that response contains token and verification_link (mocked)
        if "token" not in response or "verification_link" not in response:
            self.log_test("Email verification response format", False, "Missing token or verification_link")
            return None, None
        
        self.log_test("Email verification response format", True)
        token = response["token"]
        
        # Step 2: Verify the token
        success, verify_response, status = self.run_test(
            "Email token verification",
            "GET",
            f"auth/verify/{token}",
            200
        )
        
        if success and "email" in verify_response:
            self.log_test("Email verification token valid", True)
            return test_email, token
        else:
            self.log_test("Email verification token valid", False, "Invalid token response")
            return None, None

    def test_complete_registration(self, email, token):
        """Test completing registration with username and password"""
        print("\n🔍 Testing Complete Registration...")
        
        test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
        test_password = "testpass123"
        
        success, response, status = self.run_test(
            "Complete registration",
            "POST",
            "auth/complete-register",
            200,
            {
                "token": token,
                "username": test_username,
                "password": test_password
            }
        )
        
        if success and "id" in response and "username" in response:
            self.log_test("Registration completion response format", True)
            self.user_token = response.get("token")
            return test_username, test_password, response["id"]
        else:
            self.log_test("Registration completion response format", False, "Missing required fields")
            return None, None, None

    def test_login_with_username(self, username, password):
        """Test login using username + password (NOT email)"""
        print("\n🔍 Testing Login with Username...")
        
        success, response, status = self.run_test(
            "Login with username+password",
            "POST",
            "auth/login",
            200,
            {
                "username": username,
                "password": password
            }
        )
        
        if success and "token" in response:
            self.log_test("Login response contains token", True)
            self.user_token = response["token"]
            return True
        else:
            self.log_test("Login response contains token", False, "No token in response")
            return False

    def test_admin_verification(self):
        """Test admin control panel password verification"""
        print("\n🔍 Testing Admin Control Panel...")
        
        # Test with correct admin password
        success, response, status = self.run_test(
            "Admin password verification",
            "POST",
            "admin/verify",
            200,
            {"password": "F1RE88HAMZA8ADMIN"}
        )
        
        if success and "admin_token" in response:
            self.log_test("Admin token received", True)
            self.admin_token = response["admin_token"]
            return True
        else:
            self.log_test("Admin token received", False, "No admin_token in response")
            return False

    def test_admin_users_list(self):
        """Test admin users list endpoint"""
        if not self.admin_token:
            self.log_test("Admin users list", False, "No admin token available")
            return False
            
        print("\n🔍 Testing Admin Users List...")
        
        success, response, status = self.run_test(
            "Get admin users list",
            "GET",
            "admin/users",
            200,
            headers={"X-Admin-Token": self.admin_token}
        )
        
        if success and isinstance(response, list):
            self.log_test("Admin users list format", True)
            
            # Check if users have plain_password field
            has_plain_password = False
            for user in response:
                if "plain_password" in user:
                    has_plain_password = True
                    break
            
            if has_plain_password:
                self.log_test("Users have plain_password field", True)
            else:
                self.log_test("Users have plain_password field", False, "No plain_password field found")
            
            return True
        else:
            self.log_test("Admin users list format", False, "Response is not a list")
            return False

    def test_existing_admin_login(self):
        """Test login with existing admin account"""
        print("\n🔍 Testing Existing Admin Login...")
        
        success, response, status = self.run_test(
            "Admin account login",
            "POST",
            "auth/login",
            200,
            {
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if success:
            self.log_test("Admin login successful", True)
            return True
        else:
            self.log_test("Admin login successful", False, f"Status: {status}")
            return False

    def test_invalid_login_attempts(self):
        """Test invalid login attempts and brute force protection"""
        print("\n🔍 Testing Invalid Login Protection...")
        
        # Test with wrong password
        success, response, status = self.run_test(
            "Invalid password rejection",
            "POST",
            "auth/login",
            401,
            {
                "username": "admin",
                "password": "wrongpassword"
            }
        )
        
        return success

    def test_friend_endpoints(self):
        """Test friend-related endpoints"""
        if not self.user_token:
            print("⚠️ Skipping friend tests - no user token")
            return
            
        print("\n🔍 Testing Friend Endpoints...")
        
        # Test friend search
        success, response, status = self.run_test(
            "Friend search endpoint",
            "GET",
            "friends/search?q=admin",
            200,
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        # Test get friends list
        success, response, status = self.run_test(
            "Get friends list",
            "GET",
            "friends",
            200,
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        # Test get friend requests
        success, response, status = self.run_test(
            "Get friend requests",
            "GET",
            "friends/requests",
            200,
            headers={"Authorization": f"Bearer {self.user_token}"}
        )

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting F1RECHAT Backend API Tests...")
        print(f"Testing against: {self.base_url}")
        
        # Test 1: Multi-step registration flow
        email, token = self.test_email_verification_flow()
        
        if email and token:
            # Test 2: Complete registration
            username, password, user_id = self.test_complete_registration(email, token)
            
            if username and password:
                # Test 3: Login with username
                self.test_login_with_username(username, password)
        
        # Test 4: Existing admin login
        self.test_existing_admin_login()
        
        # Test 5: Admin control panel
        self.test_admin_verification()
        self.test_admin_users_list()
        
        # Test 6: Invalid login protection
        self.test_invalid_login_attempts()
        
        # Test 7: Friend endpoints
        self.test_friend_endpoints()
        
        # Print summary
        print(f"\n📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            return 1

def main():
    tester = F1RECHATAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())