#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple test for TempMail integration."""

import sys
import time

# Mock dependencies yang dibutuhkan mail_service
class MockRequests:
    """Mock curl_cffi requests."""
    class Response:
        def __init__(self, status_code, json_data):
            self.status_code = status_code
            self._json_data = json_data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
        
        def json(self):
            return self._json_data
    
    class exceptions:
        Timeout = TimeoutError

# Inject mock
sys.modules['curl_cffi'] = type('module', (), {'requests': MockRequests()})()

import mail_service

# Test config
mail_service.config = {
    "tempmail_api_base": "https://renunganbot.qzz.io",
    "tempmail_api_key": "test-key-123",
    "tempmail_domain": "renunganbot.qzz.io",
    "user_agent": "Mozilla/5.0 Test",
}

def test_config():
    """Test config getters."""
    print("[TEST] Config getters...")
    assert mail_service.get_tempmail_api_base() == "https://renunganbot.qzz.io"
    assert mail_service.get_tempmail_api_key() == "test-key-123"
    assert mail_service.get_tempmail_domain() == "renunganbot.qzz.io"
    assert mail_service.get_email_provider() == "tempmail"
    print("✓ Config OK")

def test_username_generation():
    """Test username generator."""
    print("[TEST] Username generation...")
    username = mail_service.generate_username(10)
    assert len(username) == 10
    assert username.isalnum()
    print(f"✓ Generated: {username}")

def test_api_structure():
    """Test API function signatures."""
    print("[TEST] API structure...")
    
    # Check public interface exists
    assert hasattr(mail_service, 'get_email_and_token')
    assert hasattr(mail_service, 'get_oai_code')
    assert hasattr(mail_service, 'get_email_provider')
    
    # Check TempMail functions exist
    assert hasattr(mail_service, 'tempmail_create_inbox')
    assert hasattr(mail_service, 'tempmail_wait_for_code')
    assert hasattr(mail_service, 'tempmail_cleanup')
    
    print("✓ API structure OK")

def test_mock_http_calls():
    """Test HTTP call patterns (mocked)."""
    print("[TEST] HTTP call patterns...")
    
    # Mock http_post for create inbox
    def mock_http_post(url, **kwargs):
        if '/api/inbox' in url:
            return MockRequests.Response(200, {
                "email": "test123@renunganbot.qzz.io",
                "inbox_id": 42,
                "expires": "24h",
            })
        return MockRequests.Response(500, {})
    
    # Mock http_get for wait
    def mock_http_get(url, **kwargs):
        if '/api/inbox/' in url and '/wait' in url:
            return MockRequests.Response(200, {
                "id": 1,
                "from": "test@example.com",
                "subject": "Verification Code",
                "codes": ["123456"],
                "links": [],
                "text_body": "Your code is 123456",
            })
        return MockRequests.Response(500, {})
    
    # Mock http_delete for cleanup
    def mock_http_delete(url, **kwargs):
        return MockRequests.Response(204, {})
    
    # Inject mocks
    mail_service.http_post = mock_http_post
    mail_service.http_get = mock_http_get
    mail_service.http_delete = mock_http_delete
    
    # Test create
    email, inbox_id = mail_service.tempmail_create_inbox()
    assert email == "test123@renunganbot.qzz.io"
    assert inbox_id == 42
    print(f"✓ Create: {email}")
    
    # Test wait (with mock cancel check)
    def mock_cancel():
        return False
    
    def mock_log(msg):
        print(f"  {msg}")
    
    mail_service.raise_if_cancelled = lambda cb: None
    mail_service.sleep_with_cancel = lambda sec, cb: None
    
    code = mail_service.tempmail_wait_for_code(
        email=email,
        timeout=10,
        log_callback=mock_log,
        cancel_callback=mock_cancel,
    )
    assert code == "123456"
    print(f"✓ Wait: code={code}")
    
    # Test cleanup
    mail_service.tempmail_cleanup(email)
    print("✓ Cleanup: OK")

def main():
    """Run all tests."""
    print("=" * 60)
    print("TempMail Integration Test")
    print("=" * 60)
    
    try:
        test_config()
        test_username_generation()
        test_api_structure()
        test_mock_http_calls()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
