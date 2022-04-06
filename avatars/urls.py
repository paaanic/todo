from django.urls import path

from .views import avatar_image

app_name = 'avatars'
urlpatterns = [
    path('avatar.<str:seed>.png/', avatar_image, name='get'),
]
