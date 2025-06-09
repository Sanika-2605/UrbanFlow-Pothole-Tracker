# from django.shortcuts import render
# from django.http import FileResponse
# from ultralytics import YOLO
# from django.views.decorators.csrf import csrf_exempt
# from django.core.files.storage import default_storage
# from datetime import datetime
# import os
# from .utils.twilio_utils import send_sms
# from django.conf import settings
# from django.http import JsonResponse
# from .mongodb import pothole_collection  # Import the MongoDB collection

# model = YOLO("runs/yolov8/model1_100epoch.pt")  # adjust path to your trained model

# def officer_dashboard(request):
#     detection_root = 'runs/detect'
#     images = []

#     for folder in os.listdir(detection_root):
#         folder_path = os.path.join(detection_root, folder)
#         if os.path.isdir(folder_path):
#             for file in os.listdir(folder_path):
#                 if file.endswith('.jpg') or file.endswith('.png'):
#                     rel_path = os.path.join('detect', folder, file)
#                     images.append(rel_path)

#     images.sort(reverse=True)
#     context = {'images': images}
#     return render(request, 'officer_dashboard.html', context)

# @csrf_exempt
# def detect(request):
#     if request.method == 'POST' and request.FILES.get('image'):
#         uploaded_file = request.FILES['image']
#         image_path = default_storage.save(f"media_images/{uploaded_file.name}", uploaded_file)
#         abs_image_path = default_storage.path(image_path)

#         # Generate unique folder name using timestamp
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_folder = f"predict_{timestamp}"
#         output_dir = os.path.join("runs", "detect", output_folder)

#         # Run YOLO detection with unique folder
#         results = model.predict(
#             source=abs_image_path,
#             save=True,
#             project="runs/detect",
#             name=output_folder
#         )

#         output_image_path = os.path.join(output_dir, uploaded_file.name)

#         if len(results[0].boxes) > 0:
#             print("✅ Pothole detected!")
#             send_sms(settings.GOVT_OFFICER_PHONE,"Pothole detected! Please check the dashboard for the image and location.")

#         return FileResponse(open(output_image_path, 'rb'), content_type='image/jpg')

#     return render(request, 'upload.html')






# def report_pothole(request):
#     if request.method == "POST":
#         try:
#             data = {
#                 "user_name": request.POST.get("user_name"),
#                 "phone_number": request.POST.get("phone_number"),
#                 "location": {
#                     "lat": float(request.POST.get("lat")),
#                     "long": float(request.POST.get("long")),
#                 },
#                 "image_url": request.POST.get("image_url"),
#                 "severity": request.POST.get("severity"),
#                 "reported_at": datetime.now()
#             }

#             pothole_collection.insert_one(data)
#             return JsonResponse({"status": "success", "message": "Pothole reported!"})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)









from .mongodb import pothole_collection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, PotholeReport
from .yolo_utils import detect_pothole
from .notification import send_sms, send_alert_email
from django.core.files.storage import default_storage
from django.conf import settings
import random
import string
from django.http import JsonResponse
from datetime import datetime

@api_view(['POST'])
def request_otp(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': 'Phone number is required'}, status=400)

    # Generate random 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))

    # Store OTP in session keyed by phone number for security
    request.session[f'otp_{phone}'] = otp

    # Send OTP via SMS using Twilio
    message = f"Your OTP for Pothole Tracker is {otp}"
    sms_sent = send_sms(phone, message)

    if sms_sent:
        return Response({'message': 'OTP sent successfully'})
    else:
        return Response({'error': 'Failed to send OTP'}, status=500)

@api_view(['POST'])
def verify_otp(request):
    phone = request.data.get('phone')
    otp_input = request.data.get('otp')
    if not phone or not otp_input:
        return Response({'error': 'Phone and OTP are required'}, status=400)

    stored_otp = request.session.get(f'otp_{phone}')
    if stored_otp == otp_input:
        name = request.data.get('name', 'Anonymous')
        user, created = User.objects.get_or_create(phone=phone, defaults={'name': name})
        user.otp_verified = True
        user.save()
        # Clear OTP from session after successful verification
        del request.session[f'otp_{phone}']
        return Response({'message': 'OTP verified successfully'})
    else:
        return Response({'error': 'Invalid OTP'}, status=400)

@api_view(['POST'])
def submit_report(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': 'Phone is required'}, status=400)

    user = get_object_or_404(User, phone=phone, otp_verified=True)

    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Image file is required'}, status=400)

    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    location = request.data.get('location', '')

    if not latitude or not longitude:
        return Response({'error': 'Latitude and Longitude are required'}, status=400)

    latitude = float(latitude)
    longitude = float(longitude)

    # Save image to media storage
    saved_path = default_storage.save(f"pothole_images/{image.name}", image)

    # Detect pothole attributes using YOLO
    detection = detect_pothole(saved_path)

    report = PotholeReport.objects.create(
        user=user,
        image=saved_path,
        location=location,
        latitude=latitude,
        longitude=longitude,
        width=detection['width'],
        height=detection['height'],
        depth=detection['depth'],
        severity=detection['severity']
    )

    # Send SMS alert to user
    user_msg = f"Thank you {user.name}, your pothole report has been submitted successfully. Severity: {detection['severity']}."
    send_sms(user.phone, user_msg)

    # Compose email alert for corporator and MNC
    email_subject = f"New Pothole Report - Severity: {detection['severity'].capitalize()}"
    email_body = (
        f"Location: {location}\n"
        f"Latitude: {latitude}, Longitude: {longitude}\n"
        f"Severity: {detection['severity'].capitalize()}\n"
        f"Reported by: {user.name}, Phone: {user.phone}\n"
        f"Pothole dimensions (WxHxD): {detection['width']} x {detection['height']} x {detection['depth']}"
    )

    corporator_email = "sanikapb2316@gmail.com"
    mnc_email = "sanika.brahmankar24@vit.edu"

    send_alert_email(corporator_email, email_subject, email_body)
    send_alert_email(mnc_email, email_subject, email_body)

    return Response({'message': 'Pothole report submitted successfully', 'severity': detection['severity']})


def report_pothole(request):
    if request.method == "POST":
        try:
            data = {
                "user_name": request.POST.get("user_name"),
                "phone_number": request.POST.get("phone_number"),
                "location": {
                    "lat": float(request.POST.get("lat")),
                    "long": float(request.POST.get("long")),
                },
                "image_url": request.POST.get("image_url"),
                "severity": request.POST.get("severity"),
                "reported_at": datetime.now()
            }

            print("[DEBUG] Data received:", data)  # 👈 Add this

            pothole_collection.insert_one(data)
            return JsonResponse({"status": "success", "message": "Pothole reported!"})
        except Exception as e:
            print("[ERROR]", str(e))  # 👈 Add this
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)