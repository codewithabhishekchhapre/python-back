from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns=[
     path("abhi/",views.Hello),
     path("view/",views.my_view),
     path("login/",views.login),
     path('api/signup/', views.Signup_api, name='signup_api'),
     path('send-otp/', views.send_otp, name='send_otp'),
     path('api/create-profile/', views.create_profile),
     path('api/get-all-profiles/', views.get_All_profile),
     path('api/get-profile/<int:id>/', views.get_profile_by_user),
     path("",views.Home),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)