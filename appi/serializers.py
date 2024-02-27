from rest_framework import serializers
from .models import CustomUser, Task
from .models import Transaction, Withdrawal, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'balance', 'deliveryAddress', 'code', 'recommended_by', 'date_joined', 'account_type', 'today_earnings', 'total_earnings', 'role', 'register_ip', 'country_ip', 'allow_unaffordable_tasks']
   

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'date', 'status', 'image_url', 'user']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')  # Check if the 'request' object is part of the serializer context
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'amount', 'request_date', 'status']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'