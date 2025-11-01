import jwt
import os
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from external.smoke_api import get_jwt_token
from django.conf import settings
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('token')
        if not token:
            return None
            
        try:
            secret_key = os.getenv('SECRET_KEY')
            decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            user = AnonymousUser()
            user.username = decoded.get('username')
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Session expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')

def verify_user_with_smoked_api(username, password):
    try:
        login_payload = {"username": username, "password": password}
        token = get_jwt_token(settings.LOGIN_URL, login_payload)
        return bool(token)
    except Exception:
        return False


def create_jwt_token(username):
    """Create JWT token with username in payload"""
    import jwt
    from datetime import datetime, timedelta
    from django.conf import settings

    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt_token(token):
    """Verify JWT token and return True if valid"""
    try:
        import jwt
        from django.conf import settings

        # Decode and verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def decode_jwt_token(token):
    """Decode JWT token and return payload"""
    try:
        import jwt
        from django.conf import settings

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None