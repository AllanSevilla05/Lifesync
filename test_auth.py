#!/usr/bin/env python3
"""
Simple test script to verify LifeSync backend authentication
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_health():
    """Test if the server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Server is running!")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
        return False

def create_test_user():
    """Create a test user account"""
    user_data = {
        "email": "test@lifesync.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            print("✅ Test user created successfully!")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  Test user already exists")
            return True
        else:
            print(f"❌ Failed to create user: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def test_login():
    """Test login with the test user"""
    login_data = {
        "username": "test@lifesync.com",  # Using email as username
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Login successful!")
            print(f"🔑 Access token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Protected endpoint access successful!")
            print(f"👤 User: {user_data.get('email')} ({user_data.get('full_name')})")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")
        return False

def main():
    print("🧪 Testing LifeSync Backend Authentication")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣  Testing server health...")
    if not test_health():
        print("\n💡 Make sure to start the backend server first:")
        print("   cd lifesync_ai_backend")
        print("   python3 start_server.py")
        return
    
    # Test 2: Create test user
    print("\n2️⃣  Creating test user...")
    if not create_test_user():
        return
    
    # Test 3: Login
    print("\n3️⃣  Testing login...")
    token = test_login()
    if not token:
        return
    
    # Test 4: Protected endpoint
    print("\n4️⃣  Testing protected endpoint...")
    if test_protected_endpoint(token):
        print("\n🎉 All tests passed! Authentication is working correctly.")
        print("\n📱 Frontend login credentials:")
        print("   Email: test@lifesync.com")
        print("   Password: testpassword123")
    else:
        print("\n❌ Some tests failed.")

if __name__ == "__main__":
    main()