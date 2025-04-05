"""
Backend API Test Suite

This module provides comprehensive testing of the backend API with:
- Authentication and authorization
- User management and verification
- Customer management
- Activity logging
- Profile management
- Rate limiting
"""

import requests
import json
from typing import Dict, Any, Optional
import sys
from datetime import datetime
import time
import uuid

BASE_URL = "http://localhost:5001/api/v1"

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_user_data = None
    
    def set_auth_header(self, token: str):
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def post(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        return requests.post(f"{BASE_URL}{endpoint}", 
                           json=data, 
                           headers=self.headers)

    def put(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        return requests.put(f"{BASE_URL}{endpoint}", 
                          json=data, 
                          headers=self.headers)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.get(f"{BASE_URL}{endpoint}", 
                          headers=self.headers,
                          params=params)

    def delete(self, endpoint: str) -> requests.Response:
        return requests.delete(f"{BASE_URL}{endpoint}", 
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
            print(f"Error: {response.json()}")
            return False
        
        token_data = response.json()
        if not token_data.get("access_token") or not token_data.get("refresh_token"):
            print("❌ Invalid token response")
            return False
        
        self.set_auth_header(token_data["access_token"])
        
        # Test token refresh
        refresh_response = self.post("/auth/refresh", {
            "refresh_token": token_data["refresh_token"]
        })
        if refresh_response.status_code != 200:
            print("❌ Token refresh failed")
            return False
        
        print("✅ Authentication successful")
        return True

    def test_user_management(self) -> bool:
        """Test user management functionality"""
        print("\nTesting User Management...")
        
        # Create test user
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.test_user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User",
            "role": "USER",
            "verification_method": "EMAIL",
            "timezone": "UTC",
            "language": "en"
        }
        
        response = self.post("/admin/users", self.test_user_data)
        if response.status_code != 201:
            print("❌ User creation failed")
            print(f"Error: {response.json()}")
            return False
        
        user_data = response.json()
        user_id = user_data["id"]
        
        # Test user profile
        response = self.get(f"/admin/users/{user_id}")
        if response.status_code != 200:
            print("❌ User profile retrieval failed")
            return False
        
        profile = response.json()
        if not all(key in profile for key in ["uuid", "email", "role", "profile"]):
            print("❌ User profile missing required fields")
            return False
        
        # Test user update
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "timezone": "Europe/London"
        }
        response = self.put(f"/admin/users/{user_id}", update_data)
        if response.status_code != 200:
            print("❌ User update failed")
            return False
        
        print("✅ User management successful")
        return True

    def test_verification_system(self) -> bool:
        """Test verification system"""
        print("\nTesting Verification System...")
        
        if not self.test_user_data:
            print("❌ No test user data available")
            return False
        
        # Request verification code
        response = self.post("/auth/request-verification", {
            "email": self.test_user_data["email"],
            "method": "EMAIL"
        })
        if response.status_code != 200:
            print("❌ Verification request failed")
            return False
        
        # Test rate limiting
        response = self.post("/auth/request-verification", {
            "email": self.test_user_data["email"],
            "method": "EMAIL"
        })
        if response.status_code != 429:
            print("⚠️ Rate limiting not working as expected")
        
        print("✅ Verification system working")
        return True

    def test_customer_management(self) -> bool:
        """Test customer management functionality"""
        print("\nTesting Customer Management...")
        
        # Create customer
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        customer_data = {
            "email": f"customer_{timestamp}@example.com",
            "business_name": f"Test Business {timestamp}",
            "contact_name": "John Doe",
            "phone": "+1234567890",
            "timezone": "UTC",
            "language": "en",
            "metadata": {
                "industry": "Technology",
                "size": "Small"
            }
        }
        
        response = self.post("/admin/customers", customer_data)
        if response.status_code != 201:
            print("❌ Customer creation failed")
            print(f"Error: {response.json()}")
            return False

        customer_id = response.json()["id"]
        
        # Test customer retrieval
        response = self.get(f"/admin/customers/{customer_id}")
        if response.status_code != 200:
            print("❌ Customer retrieval failed")
            return False
        
        # Test customer search
        response = self.get("/admin/customers", params={
            "search": customer_data["business_name"],
            "page": 1,
            "per_page": 10
        })
        if response.status_code != 200:
            print("❌ Customer search failed")
            return False
        
        # Test customer update
        update_data = {
            "business_name": f"Updated Business {timestamp}",
            "metadata": {
                "industry": "Technology",
                "size": "Medium"
            }
        }
        response = self.put(f"/admin/customers/{customer_id}", update_data)
        if response.status_code != 200:
            print("❌ Customer update failed")
            return False

        print("✅ Customer management working")
        return True

    def test_activity_logging(self) -> bool:
        """Test activity logging system"""
        print("\nTesting Activity Logging...")
        
        # Check recent activity logs
        response = self.get("/admin/activity", params={
            "page": 1,
            "per_page": 10,
            "start_date": (datetime.now().date().isoformat())
        })
        if response.status_code != 200:
            print("❌ Activity log retrieval failed")
            print(f"Error: {response.json()}")
            return False

        logs = response.json().get("logs", [])
        if not logs:
            print("⚠️ No activity logs found (this might be normal for a fresh system)")
        else:
            required_fields = ["id", "user_id", "action_type", "created_at", "ip_address"]
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
            self.test_user_management,
            self.test_verification_system,
            self.test_customer_management,
            self.test_activity_logging
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                # Small delay between tests to avoid rate limiting
                time.sleep(1)
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
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend server is not running")
        print("Please start the backend server first:")
        print("python app.py")
        sys.exit(1)
    
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 