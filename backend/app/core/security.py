import hashlib
import secrets
import time
from collections import defaultdict
from typing import Dict, Tuple

# Sliding window rate limiter for OTP requests (Max 3 OTP requests per phone per 10 mins)
# Key: phone number -> list of timestamps
_otp_rate_limit_cache: Dict[str, list] = defaultdict(list)

def check_otp_rate_limit(phone: str, max_requests: int = 3, window_seconds: int = 600) -> Tuple[bool, int]:
    """
    Verifies that a phone number has not exceeded the OTP request quota.
    Returns (allowed: bool, retry_after_seconds: int)
    """
    now = time.time()
    clean_phone = phone.strip()[-10:] # Last 10 digits
    timestamps = _otp_rate_limit_cache[clean_phone]
    
    # Prune old timestamps
    _otp_rate_limit_cache[clean_phone] = [t for t in timestamps if now - t < window_seconds]
    current_count = len(_otp_rate_limit_cache[clean_phone])
    
    if current_count >= max_requests:
        oldest = _otp_rate_limit_cache[clean_phone][0]
        retry_after = int(window_seconds - (now - oldest))
        return False, max(1, retry_after)
    
    _otp_rate_limit_cache[clean_phone].append(now)
    return True, 0

def generate_secure_otp(length: int = 6) -> str:
    """Generates a cryptographically strong numeric OTP."""
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))

def hash_otp(otp: str, salt: str) -> str:
    """Hashes the OTP with salt so plain OTP is never stored directly in the database."""
    return hashlib.sha256(f"{salt}:{otp}".encode("utf-8")).hexdigest()

def mask_phone(phone: str) -> str:
    """Masks phone number for safe PII logging and display (e.g., +91 98*** **210)."""
    if len(phone) < 10:
        return "***"
    return f"+91 {phone[:2]}*** **{phone[-3:]}"

def mask_email(email: str) -> str:
    """Masks email for safe PII logging and display (e.g., su***@gmail.com)."""
    if "@" not in email:
        return "***"
    user, domain = email.split("@", 1)
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[:2] + "*" * (len(user) - 2)
    return f"{masked_user}@{domain}"
