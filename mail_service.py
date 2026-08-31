"""TempMail By JhopanStore integration - simple and efficient email service."""
import re
import secrets
import string
import time
from typing import Optional, Callable
from curl_cffi import requests

config = {}


def bind_runtime(namespace):
    global config
    config = namespace.get("config", config)
    for name, value in namespace.items():
        if name.startswith("__") or name == "config":
            continue
        globals()[name] = value


def generate_username(length=10):
    """Generate random username for email."""
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def get_tempmail_api_base():
    """Get TempMail API base URL."""
    return str(config.get("tempmail_api_base", "")).rstrip("/")


def get_tempmail_api_key():
    """Get TempMail API key."""
    return str(config.get("tempmail_api_key", "")).strip()


def get_tempmail_domain():
    """Get TempMail domain."""
    return str(config.get("tempmail_domain", "")).strip()


def get_user_agent():
    """Get user agent string."""
    return config.get(
        "user_agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    )


def tempmail_create_inbox(username=None):
    """
    Create temporary inbox via TempMail API.
    
    Returns:
        tuple: (email_address, inbox_id)
    """
    api_base = get_tempmail_api_base()
    api_key = get_tempmail_api_key()
    domain = get_tempmail_domain()
    
    if not api_base:
        raise Exception("TempMail API Base未配置")
    if not api_key:
        raise Exception("TempMail API Key未配置")
    if not domain:
        raise Exception("TempMail Domain未配置")
    
    headers = {
        "Content-Type": "application/json",
        "X-Email-API-Key": api_key,
    }
    
    payload = {"domain": domain}
    if username:
        payload["username"] = username
    
    try:
        resp = http_post(
            f"{api_base}/api/inbox",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        
        email = data.get("email")
        inbox_id = data.get("inbox_id")
        
        if not email:
            raise Exception(f"TempMail创建邮箱失败，缺少email字段: {data}")
        
        return email, inbox_id
    except Exception as exc:
        raise Exception(f"TempMail创建邮箱失败: {exc}")


def tempmail_wait_for_code(
    email,
    timeout=180,
    log_callback=None,
    cancel_callback=None,
    resend_callback=None,
):
    """
    Wait for verification code using TempMail blocking wait endpoint.
    
    This is much more efficient than polling - server blocks until email arrives.
    """
    api_base = get_tempmail_api_base()
    api_key = get_tempmail_api_key()
    
    if not api_base:
        raise Exception("TempMail API Base未配置")
    if not api_key:
        raise Exception("TempMail API Key未配置")
    
    headers = {"X-Email-API-Key": api_key}
    
    # TempMail /wait endpoint blocks server-side until email arrives
    # Much better than client polling loop
    deadline = time.time() + timeout
    wait_timeout = min(60, timeout)  # Max 60s per request to allow resend checks
    
    while time.time() < deadline:
        raise_if_cancelled(cancel_callback)
        
        # Check if we should trigger resend
        if resend_callback and time.time() >= (deadline - timeout + 35):
            try:
                resend_callback()
                if log_callback:
                    log_callback("[*] 已触发重新发送验证码")
            except Exception as exc:
                if log_callback:
                    log_callback(f"[Debug] 触发重发失败: {exc}")
        
        try:
            remaining = int(deadline - time.time())
            if remaining <= 0:
                break
            
            current_timeout = min(wait_timeout, remaining)
            
            if log_callback:
                log_callback(f"[*] 等待邮件中 (timeout={current_timeout}s)...")
            
            resp = http_get(
                f"{api_base}/api/inbox/{email}/wait",
                params={"timeout": current_timeout},
                headers=headers,
                timeout=current_timeout + 10,  # Add buffer for network
            )
            
            resp.raise_for_status()
            data = resp.json()
            
            # TempMail auto-extracts codes and links server-side
            codes = data.get("codes", [])
            subject = data.get("subject", "")
            from_addr = data.get("from", "")
            
            if log_callback:
                log_callback(f"[*] 收到邮件: {subject} (发件人: {from_addr})")
            
            if codes and len(codes) > 0:
                code = codes[0]
                if log_callback:
                    log_callback(f"[*] 提取到验证码: {code}")
                return code
            
            # No code in this email, continue waiting
            if log_callback:
                log_callback("[Debug] 邮件中未提取到验证码，继续等待...")
                
        except requests.exceptions.Timeout:
            # Server timeout, retry with remaining time
            if log_callback:
                log_callback("[Debug] 等待超时，重试...")
            continue
        except Exception as exc:
            if log_callback:
                log_callback(f"[Debug] TempMail等待失败: {exc}")
            # Small delay before retry on error
            sleep_with_cancel(3, cancel_callback)
            continue
    
    raise Exception(f"TempMail在{timeout}s内未收到验证码")


def tempmail_cleanup(email):
    """Delete all messages in an inbox."""
    api_base = get_tempmail_api_base()
    api_key = get_tempmail_api_key()
    
    if not api_base or not api_key:
        return  # Skip cleanup if not configured
    
    headers = {"X-Email-API-Key": api_key}
    
    try:
        http_delete(
            f"{api_base}/api/inbox/{email}",
            headers=headers,
            timeout=10,
        )
    except Exception:
        pass  # Cleanup is best-effort


# Public interface matching existing mail_service contract
def get_email_and_token(api_key=None):
    """
    Create temporary email inbox.
    
    Returns:
        tuple: (email_address, token)
        Note: token is just inbox_id for TempMail, not used in wait endpoint
    """
    email, inbox_id = tempmail_create_inbox()
    return email, str(inbox_id)


def get_oai_code(
    dev_token,
    email,
    timeout=180,
    poll_interval=3,  # Not used with TempMail's blocking wait
    log_callback=None,
    cancel_callback=None,
    resend_callback=None,
):
    """
    Wait for verification code from email.
    
    Args:
        dev_token: Not used by TempMail (API key from config)
        email: Email address to monitor
        timeout: Max seconds to wait
        poll_interval: Ignored (TempMail uses blocking wait)
        log_callback: Optional logging function
        cancel_callback: Optional cancellation check
        resend_callback: Optional resend trigger
    """
    return tempmail_wait_for_code(
        email=email,
        timeout=timeout,
        log_callback=log_callback,
        cancel_callback=cancel_callback,
        resend_callback=resend_callback,
    )


def get_email_provider():
    """Return provider name - always tempmail now."""
    return "tempmail"
