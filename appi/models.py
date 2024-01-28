from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models import F

import random
import string
from django.contrib.auth.hashers import make_password

from .utils import generate_ref_code
from decimal import Decimal

class CustomUser(AbstractUser):
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('housekeeping', 'Housekeeping'),
        ('hr', 'Hr'),
    ]

    username = models.CharField(unique=True, max_length=150)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    password = models.CharField(max_length=128, default=make_password(''), blank=True)
    deliveryAddress = models.CharField(max_length=42, null=True)
    code = models.CharField(max_length=8, blank=True)
    recommended_by = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='ref_by')
    last_address_update = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(default=timezone.now)
    allow_unaffordable_tasks = models.BooleanField(default=False)
    
    pending_tasks = models.ManyToManyField('Task', related_name='pending_tasks')  # Change here
    tasks_done_today = models.PositiveIntegerField(default=0)
    tasks_left_today = models.PositiveIntegerField(default=5)
    last_task_completion_date = models.DateField(null=True, blank=True)
    today_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed_tasks_count = models.PositiveIntegerField(default=0)
    completed_tasks_current_cycle = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_country = models.CharField(max_length=100, null=True, blank=True)
    register_ip = models.CharField(max_length=100, null=True, blank=True)
    country_ip = models.CharField(max_length=100, null=True, blank=True)
    
    is_demo_account = models.BooleanField(default=False)
    demo_account_expiration = models.DateTimeField(null=True, blank=True)
    real_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='demo_accounts')

    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='user')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Change to Decimal for precision
    hold_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Change to Decimal for precision
    account_type = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'), 
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond')],
        default='bronze')
    
    def reset_daily_tasks(self):
        if self.last_task_completion_date != timezone.localdate():
            self.last_task_completion_date = timezone.localdate()
            self.tasks_done_today = 0
            self.completed_tasks_current_cycle = 0
            self.allow_unaffordable_tasks = True

            
            if self.account_type == 'bronze':
                self.tasks_left_today = 20
            elif self.account_type == 'silver':
                self.tasks_left_today = 30
            elif self.account_type == 'gold':
                self.tasks_left_today = 40
            elif self.account_type == 'platinum':
                self.tasks_left_today = 50
            elif self.account_type == 'diamond':
                self.tasks_left_today = 60

            self.save()
            

    def __str__(self):
        return f"{self.username}={self.code}"
    
    def get_recommended_profiles(self):
        pass

class Notification(models.Model):
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        # Add more types as needed
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info')
    title = models.CharField(max_length=150)
    content = models.TextField()
    link = models.URLField(blank=True, null=True)  # Optional field to hold a link related to the notification
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

   
class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    task_type = models.CharField(max_length=265)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete'), ('frozen', 'Frozen')], default='pending')
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add the commission field here
    image = models.URLField(default='') 
    created_at = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True)
    

    def calculate_commission(self):
        if self.status == 'complete':
            # Add the commission to the user's balance
            commission_amount = Decimal(self.price) * (Decimal(self.commission_percentage) / 100)

            self.user.balance += commission_amount  # Update user balance
            self.user.today_earnings += commission_amount  # Update today's earnings
            self.user.total_earnings += commission_amount  # Update total earnings
            self.user.save()  # Important: save the user instance to persist the changes to the database

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Task.objects.get(pk=self.pk)
            if orig.status != 'complete' and self.status == 'complete':
                self.calculate_commission()

        super(Task, self).save(*args, **kwargs)

class TaskConfiguration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='task_configurations')
    account_type = models.CharField(max_length=20, choices=[
        ('bronze', 'Bronze'), 
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
        ('diamond', 'Diamond')],
        default='bronze')
    count = models.PositiveIntegerField(null=True, blank=True)  # For unaffordable tasks
    price_range_low = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_range_high = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'account_type')







class Transaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_DENIED = 'denied'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_DENIED, 'Denied'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)  # Set default to the ID of an existing CustomUser record
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    image = models.ImageField(upload_to='transactions/', null=True, blank=True)

    def __str__(self):
        return f"Transaction ID: {self.pk}, Amount: {self.amount}, User: {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Check if transaction status was changed to 'approved'
        if self.pk is not None:
            orig = Transaction.objects.get(pk=self.pk)
            if orig.status != self.STATUS_APPROVED and self.status == self.STATUS_APPROVED:
                # transaction status has just been changed to 'approved'
                # update the user balance
                self.user.balance += self.amount
                self.user.save()

        super(Transaction, self).save(*args, **kwargs)


class Withdrawal(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_DENIED = 'denied'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_DENIED, 'Denied'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"Withdrawal ID: {self.pk}, Amount: {self.amount}, User: {self.user.username}"

    def save(self, *args, **kwargs):
        # Check if withdrawal status was changed to 'approved'
        if self.pk is not None:
            orig = Withdrawal.objects.get(pk=self.pk)
            if orig.status != self.STATUS_APPROVED and self.status == self.STATUS_APPROVED:
                # withdrawal status has just been changed to 'approved'
                # update the user balance
                self.user.balance -= self.amount
                self.user.save()

        super(Withdrawal, self).save(*args, **kwargs)



class TelegramNotificationConfig(models.Model):
    send_telegram_notification = models.BooleanField(default=False)

    def __str__(self):
        return f"Send Telegram Notifications: {'Enabled' if self.send_telegram_notification else 'Disabled'}"        


class HotWallet(models.Model):
    address = models.CharField(max_length=42)
    private_key = models.CharField(max_length=66)  # Do NOT expose this in APIs
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)







        


# class UserAnalyticsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         return Response({
#             "today_income": str(user.today_earnings),
#             "personal_earnings": str(user.total_earnings),
#             "completed_orders": user.task_set.filter(is_completed=True).count(),
#             "locked_orders": user.task_set.filter(is_completed=False).count(),
#             "unfinished_orders": user.pending_tasks.filter(is_completed=False).count(),
#             "frozen_amount": str(user.balance),
#         }, status=status.HTTP_200_OK)
