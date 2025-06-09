# from django.urls import path
# from .views import detect
# from . import views


# urlpatterns = [
#     path('', detect),
#     path('detect/', detect),
#     path('report/', views.report_pothole, name='report_pothole'),
# ]







from django.urls import path
from . import views

urlpatterns = [
    path('request-otp/', views.request_otp, name='request_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('submit-report/', views.submit_report, name='submit_report'),
]