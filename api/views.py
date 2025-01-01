import jwt
import redis
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Connect to Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

# Generate JWT
def generate_jwt(mobile_number):
    payload = {
        'mobile_number': mobile_number,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

# Validate OTP
def validate_otp_logic(mobile_number, otp):
    return otp == "1234"  # Replace with real OTP logic

@api_view(['POST'])
def validate_otp(request):
    mobile_number = request.data.get('mobile_number')
    otp = request.data.get('otp')

    if validate_otp_logic(mobile_number, otp):
        token = generate_jwt(mobile_number)

        # Save JWT to Redis, replacing any existing session
        redis_client.set(mobile_number, token, ex=3600)

        return JsonResponse({'success': True, 'token': token})
    return JsonResponse({'error': 'Invalid OTP'}, status=400)


@api_view(['POST'])
def check_session(request):
    token = request.headers.get('Authorization')
    if not token:
        return JsonResponse({'error': 'Authorization header missing'}, status=401)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        mobile_number = payload['mobile_number']

        # Check Redis for a valid session
        stored_token = redis_client.get(mobile_number)
        if stored_token and stored_token.decode('utf-8') == token:
            return JsonResponse({'success': True, 'mobile_number': mobile_number})
        return JsonResponse({'error': 'Invalid session'}, status=401)
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)


@api_view(['POST'])
def logout(request):
    token = request.headers.get('Authorization')
    if not token:
        return JsonResponse({'error': 'Authorization header missing'}, status=401)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        mobile_number = payload['mobile_number']

        # Remove session from Redis
        redis_client.delete(mobile_number)
        return JsonResponse({'success': True, 'message': 'Logged out successfully'})
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)
