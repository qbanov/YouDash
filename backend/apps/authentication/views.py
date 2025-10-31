from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .jwt_auth import verify_user_with_smoked_api, create_jwt_token
from core.validators import validate_string_length, sanitize_input
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        username = sanitize_input(request.data.get('username'))
        password = request.data.get('password')
        
        valid, error = validate_string_length(username, "Username", min_length=3, max_length=50)
        if not valid:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        valid, error = validate_string_length(password, "Password", min_length=1, max_length=255)
        if not valid:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if verify_user_with_smoked_api(username, password):
            token = create_jwt_token(username)
            response = Response({"success": True, "message": "Login successful"})
            response.set_cookie(
                'token', 
                token, 
                httponly=True, 
                samesite='Lax',
                max_age=28800
            )
            logger.info(f"User {username} logged in successfully")
            return response
        else:
            logger.warning(f"Failed login attempt for user {username}")
            return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return Response({"error": "An error occurred during login"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def logout(request):
    logger.info("User logged out")
    response = Response({"success": True, "message": "Logged out successfully"})
    response.set_cookie('token', '', expires=0)
    return response
