"""
URL configuration for PracticeProj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from files.views import FileProcessingHistoryView, FileStatusView, FileUploadView, FilesListView, FileUpdateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'files', FilesListView, basename='files')
router.register(r'processing-history', FileProcessingHistoryView, basename='file_history')
router.register(r'files', FileStatusView, basename='file_status')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/file-upload', FileUploadView.as_view(), name='file_upload'),
    path('api/<str:pk>/file-update', FileUpdateView.as_view(), name='file_update'),
    # path("api/files/<str:pk>/status/", FileStatusView.as_view(), name="file-status",),
    # path('api/files/<str:pk>/status', FileStatusView.as_view(), name='file_status'),


    # path('api/file/list/', FilesListView.as_view(), name='file_list')

    # 1. file list API
    # 2. processing history list API
    # 3. Create API endpoint for file upload (images, PDFs, CSVs).

    # path('api/', include('drf_practice.urls')),
    # path('health/', include('drf_practice.urls')),
    # path('api/', include('ecom.urls')),
]
