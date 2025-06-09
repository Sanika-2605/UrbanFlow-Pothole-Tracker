from rest_framework import serializers
from .models import User, PotholeReport

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PotholeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PotholeReport
        fields = '__all__'