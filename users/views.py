from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from rql_filter.backend import RQLFilterBackend

from users.serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (RQLFilterBackend,)
