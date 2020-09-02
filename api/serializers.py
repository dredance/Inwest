from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Projekt, KamienieMilowe


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email']
