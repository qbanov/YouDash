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

def create_jwt_token(username=None):
    secret_key = os.getenv('SECRET_KEY')
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=8),
        'iat': datetime.now(timezone.utc)
    }
    if username:
        payload['username'] = username
    
    return jwt.encode(payload, secret_key, algorithm='HS256')
