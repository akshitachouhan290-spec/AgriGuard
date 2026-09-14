import os, base64, hashlib, hmac, json, secrets
SECRET = os.getenv('SECRET_KEY', 'dev-secret-change-me').encode()

def hash_password(password: str) -> str:
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120000).hex()
    return f'{salt}${digest}'

def verify_password(password: str, stored: str) -> bool:
    try:
        salt,digest=stored.split('$',1)
        actual=hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120000).hex()
        return hmac.compare_digest(actual,digest)
    except Exception: return False

def create_token(farmer_id: int) -> str:
    payload=base64.urlsafe_b64encode(json.dumps({'sub':farmer_id}).encode()).decode().rstrip('=')
    sig=hmac.new(SECRET,payload.encode(),hashlib.sha256).hexdigest()
    return f'{payload}.{sig}'
