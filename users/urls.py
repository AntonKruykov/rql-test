from django.urls import path
from rest_framework import routers

from users.views import UserViewSet, api_root

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = router.urls
urlpatterns += [
    path('', api_root),
]
