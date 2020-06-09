"""Education URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path,include
from e_learning.forms import UserCreationForm1
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = 'VirtualClass admin'
admin.site.site_title = 'VirtualClass admin'
#admin.site.site_url = 'http://coffeehouse.com/'
admin.site.index_title = 'VirtualClass administration'
admin.empty_value_display = '**Empty**'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('e_learning.urls', namespace='e_learning')),
    path('subject_overview/<slug>/', include('e_learning.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='users/login.html', authentication_form=UserCreationForm1), name='login'),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif getattr(settings, 'FORCE_SERVE_STATIC', False):
    settings.DEBUG = True
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    settings.DEBUG = False

handler404 = 'e_learning.views.error_404_view'

