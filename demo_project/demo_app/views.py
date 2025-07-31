from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import re
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from twilio.rest import Client
from uuid import uuid4
# Create your views here.


   




def Hello(request):
     return HttpResponse("this is a first view ")

def Home(request):
     template = loader.get_template('new.html')
     return HttpResponse(template.render())
 
@csrf_exempt
def login(request):
    if request.method=="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if len(username) < 3 or len(password) < 3:
            return JsonResponse({"status": "error", "message": "Username and password must be at least 3 characters long"}, status=400)
        
        if username == "admin" and password == "admin":
            return JsonResponse({"status": "success", "message": "Login successful!", "username": username})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)
        

def my_view(request):
    data = {
        'name': 'Abhishek',
        'age': 25,
        'skills': ['Python', 'Django', 'React']
    }
    return JsonResponse(data)

def send_sms_via_twilio(to_number, message):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print("Message SID:", message.sid)
        return True
    except Exception as e:
        print("Error sending SMS:", str(e))
        return False

def send_email_via_sendgrid(to_email, subject, message):
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(str(e))
        return False

users=[]

@csrf_exempt
def Signup_api(request):
     if request.method=="POST":
          userid=request.POST.get("userid")
          name=request.POST.get("name");
          email=request.POST.get("email");
          password=request.POST.get("password");
          mobile=request.POST.get("mobile");
          print(name,email,password,mobile)
          
          if not all([name, email, password, mobile]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
           
          users.append({
                'name': name,
                'email': email,
                'password': password,  # Normally, you should hash passwords
                'mobile': mobile,
                "userid": userid
            }) 
          
          return JsonResponse({'status': 'success', 'message': 'User registered successfully', 'users': users})
     
     return JsonResponse({'status': 'failed', 'message': 'User registered failed'})





# ✅ Function to generate a strong 6-digit OTP
def generate_otp():
    return random.randint(100000, 999999)

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            email = data.get('email')
            mobile = data.get('mobile')
            otp_type = data.get('otp_type')  # 'email' or 'mobile'

            # ✅ Validate otp_type
            if otp_type not in ['email', 'mobile']:
                return JsonResponse({"status": "error", "message": "Invalid otp_type. Use 'email' or 'mobile'."}, status=400)

            # ✅ Validate based on otp_type
            if otp_type == 'email':
                if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return JsonResponse({"status": "error", "message": "Invalid or missing email."}, status=400)

            if otp_type == 'mobile':
                if not mobile or not re.match(r"^\d{10}$", mobile):
                    return JsonResponse({"status": "error", "message": "Invalid or missing mobile number."}, status=400)

            # ✅ Generate OTP
            otp = generate_otp()

            # ✅ Send OTP via Email
            if otp_type == 'email' and email:
                 print(f"Send email to {email}: Your OTP is {otp}")
                 send_email_via_sendgrid(
                  to_email=email,
                  subject="Your OTP Code",
                  message=f"Your OTP is {otp}"
                  )

            # ✅ Send OTP via SMS (Print in console for now)
            if otp_type == 'mobile' and mobile:
                formatted_number = f"+91{mobile}"  # Add country code (example: India)
                sms_status = send_sms_via_twilio(
                to_number=formatted_number,
                 message=f"Your OTP is {otp}"
                )
                if not sms_status:
                  return JsonResponse({"status": "error", "message": "Failed to send SMS"}, status=500)

            return JsonResponse({
                "status": "success",
                "message": f"OTP sent successfully to {otp_type}.",
                "otp": otp  # ❗ Remove this in production for security
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


user_profiles = []

# this is profile view
@csrf_exempt
def create_profile(request):
    if request.method == 'POST':
        try:
            userid = request.POST.get("userid")
            profilephoto = request.FILES.get("profilephoto")

            if not userid or not profilephoto:
                return JsonResponse({"error": "userid and profilephoto are required"}, status=400)

            # Save profile photo
            profilephoto_name = f"profile_{uuid4().hex}_{profilephoto.name}"
            profilephoto_path = os.path.join(settings.MEDIA_ROOT, 'profile_photos', profilephoto_name)
            os.makedirs(os.path.dirname(profilephoto_path), exist_ok=True)
            with open(profilephoto_path, 'wb+') as destination:
                for chunk in profilephoto.chunks():
                    destination.write(chunk)

            # Optional: cover photo
            coverphoto = request.FILES.get("coverphoto")
            coverphoto_url = ""
            if coverphoto:
                coverphoto_name = f"cover_{uuid4().hex}_{coverphoto.name}"
                coverphoto_path = os.path.join(settings.MEDIA_ROOT, 'cover_photos', coverphoto_name)
                os.makedirs(os.path.dirname(coverphoto_path), exist_ok=True)
                with open(coverphoto_path, 'wb+') as destination:
                    for chunk in coverphoto.chunks():
                        destination.write(chunk)
                coverphoto_url = request.build_absolute_uri(f"/media/cover_photos/{coverphoto_name}")

            # Build profile dictionary
            profile = {
                "userid": int(userid),
                "profilephoto": request.build_absolute_uri(f"/media/profile_photos/{profilephoto_name}"),
                "coverphoto": coverphoto_url,
                "skills": request.POST.get("skills", "[]"),
                "experience": request.POST.get("experience", ""),
                "current_company": request.POST.get("current_company", ""),
                "bio": request.POST.get("bio", ""),
                "interest": request.POST.get("interest", "[]"),
                "hobbies": request.POST.get("hobbies", "[]")
            }

            user_profiles.append(profile)

            return JsonResponse({"message": "Profile created", "profile": profile}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
@csrf_exempt  # Disable CSRF for testing only
def get_All_profile(request):
    if request.method == 'GET':
        print("Fetching all user profiles")
        if not user_profiles:
            return JsonResponse({"message": "No profiles found"}, status=404)
        return JsonResponse({"profiles": user_profiles}, status=200)
    return JsonResponse({"error": "Only GET method allowed"}, status=405)
    
    
@csrf_exempt
def get_profile_by_user(request, id):
    if request.method == 'GET':
        try:
            # Search for the profile by userid (cast to int for comparison)
            profile = next((p for p in user_profiles if int(p["userid"]) == id), None)

            if profile:
                return JsonResponse({"profile": profile}, status=200)
            else:
                return JsonResponse({"error": "Profile not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only GET method allowed"}, status=405) 