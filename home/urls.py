from django.urls import path
from home import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index, name='home'),
    path("home/", views.index, name='home'),
    path("about/", views.about, name='about'),
    path("oncall/", views.oncall, name='oncall'),
    path("oncall/upload_file/", views.upload_file, name='upload_file'),
    path("oncall/<str:message>/", views.oncall, name='oncall'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]