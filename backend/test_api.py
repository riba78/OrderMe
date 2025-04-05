import requests
import json
from typing import Dict, Any
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def set_auth_header(self, token: str):
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        return requests.post(f"{BASE_URL}{endpoint}", 
                           json=data, 
                           headers=self.headers)

    def get(self, endpoint: str) -> requests.Response:
        return requests.get(f"{BASE_URL}{endpoint}", 
                          headers=self.headers)

    def test_auth(self) -> bool:
        """Test authentication endpoints"""
        print("\nTesting Authentication...")
        
        # Test login with admin
        login_data = {
            "email": "admin@orderme.com",
            "password": "admin123"
        }
        response = self.post("/auth/login", login_data)
        if response.status_code != 200:
            print("❌ Admin login failed")
            return False
        
        token = response.json().get("token")
        if not token:
            print("❌ No token received")
            return False
        
        self.set_auth_header(token)
        print("✅ Authentication successful")
        return True

    def test_user_verification(self) -> bool:
        """Test user verification methods"""
        print("\nTesting User Verification...")
        
        # Test user creation with verification
        test_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        new_user = {
            "email": test_email,
            "password": "test123",
            "verification_method": "email",
            "first_name": "Test",
            "last_name": "User"
        }
        response = self.post("/users", new_user)
        if response.status_code != 201:
            print("❌ User creation failed")
            print(f"Error: {response.json()}")
            return False

        user_id = response.json().get("id")
        
        # Check verification status
        response = self.get(f"/users/{user_id}/verification")
        if response.status_code != 200:
            print("❌ Verification status check failed")
            print(f"Error: {response.json()}")
            return False

        # Check user profile creation
        response = self.get(f"/users/{user_id}/profile")
        if response.status_code != 200:
            print("❌ User profile check failed")
            print(f"Error: {response.json()}")
            return False

        print("✅ User verification system working")
        return True

    def test_customer_management(self) -> bool:
        """Test customer management functionality"""
        print("\nTesting Customer Management...")
        
        # Create a customer with timestamp to avoid duplicates
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        customer_data = {
            "email": f"customer_{timestamp}@example.com",
            "nickname": f"Test Customer {timestamp}",
            "business_name": f"Test Business {timestamp}"
        }
        response = self.post("/customers", customer_data)
        if response.status_code != 201:
            print("❌ Customer creation failed")
            print(f"Error: {response.json()}")
            return False

        customer_id = response.json().get("id")
        
        # Test customer search
        response = self.get(f"/customers/search?q={customer_data['business_name']}")
        if response.status_code != 200:
            print("❌ Customer search failed")
            print(f"Error: {response.json()}")
            return False

        # Verify customer data in response
        customers = response.json().get("customers", [])
        if not any(c.get("id") == customer_id for c in customers):
            print("❌ Created customer not found in search results")
            return False

        print("✅ Customer management working")
        return True

    def test_activity_logging(self) -> bool:
        """Test activity logging system"""
        print("\nTesting Activity Logging...")
        
        # Check recent activity logs
        response = self.get("/admin/activity?limit=10")
        if response.status_code != 200:
            print("❌ Activity log retrieval failed")
            print(f"Error: {response.json()}")
            return False

        logs = response.json().get("logs", [])
        if not logs:
            print("⚠️ No activity logs found (this might be normal for a fresh system)")
        else:
            # Verify log structure
            required_fields = ["id", "user_id", "action", "created_at"]
            if not all(all(field in log for field in required_fields) for log in logs):
                print("❌ Activity logs missing required fields")
                return False

        print("✅ Activity logging system working")
        return True

    def run_all_tests(self):
        """Run all tests and report results"""
        print("Starting API Tests...")
        
        if not self.test_auth():
            print("\n❌ Tests failed at authentication")
            return False
            
        tests = [
            self.test_user_verification,
            self.test_customer_management,
            self.test_activity_logging
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with error: {str(e)}")
                results.append(False)
        
        success = all(results)
        print("\nTest Summary:")
        print("=" * 50)
        print(f"Total Tests: {len(results)}")
        print(f"Passed: {sum(results)}")
        print(f"Failed: {len(results) - sum(results)}")
        print("=" * 50)
        print("✅ All tests passed!" if success else "❌ Some tests failed")
        return success

if __name__ == "__main__":
    print("Backend API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend server is not running")
        print("Please start the backend server first:")
        print("python app.py")
        sys.exit(1)
    
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 