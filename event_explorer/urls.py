"""
URL configuration for event_explorer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.urls import path
from django.urls import include

from event_explorer.data_loader import load_data

urlpatterns = [
    path("", include("interface.urls")),
#    path('admin/', admin.site.urls),
]

base_folder = "data/" # change to file path if needed
data = {"user_study_pwa_en": load_data(base_folder+"user_study_pwa_en/v4"),
        "user_study_bing_en": load_data(base_folder + "user_study_bing_en/v1"),
        "elections_bing_en": load_data(base_folder + "elections_bing_en/v2")
        }


#/
#premio_arquivo_pt -> ""
#pwa userstudy -> Short description for the article reader
#bing userstudy -> Short description for the article reader
#bing elections -> map


