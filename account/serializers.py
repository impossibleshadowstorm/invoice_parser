from account.models import User
from rest_framework import serializers
from djoser.serializers import  UserSerializer

class CustomUserSerializer(UserSerializer):
    """
    Custom User serializer
    """

    fullname = serializers.SerializerMethodField()
    
    def get_fullname(seelf, instance):
        return instance.fullname


    class Meta:
        model = User
        fields = ("id", "email", "fullname", "is_active")