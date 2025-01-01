from django.urls import path
from .views import validate_otp, check_session, logout

urlpatterns = [
    path('validate-otp/', validate_otp, name='validate_otp'),
    path('check-session/', check_session, name='check_session'),
    path('logout/', logout, name='logout'),
]
