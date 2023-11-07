from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import generics

from datetime import datetime
import re

from .models import CustomUser, Task, Transaction, Withdrawal, Notification, TaskConfiguration, TelegramNotificationConfig
from .serializers import *
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import Token

from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import TaskSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action

from django.utils.decorators import method_decorator
from rest_framework import parsers
from django.core.exceptions import ValidationError
from itertools import chain

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .utils import generate_ref_code
from django.views import View
from rest_framework.views import APIView
import os
from decimal import Decimal
from django.db import transaction as db_transaction
import requests

import random
from django.core.files.base import ContentFile
from django.http import HttpResponse
from pathlib import Path
import json
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

from rest_framework.exceptions import APIException
from appi.permissions import IsHousekeepingOrHR, IsOwnerOfNotification, IsHR



######userviews######


#gets user info once user logs in, NEED TO MAKE SURE THIS IS SET UP CORRECTLY WITH JWT!!!!!!!!!!
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@api_view(['GET'])
def user_detail(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # Serialize user details
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "balance": str(user.balance),
        "hold_balance": str(user.hold_balance),
        "deliveryAddress": user.deliveryAddress or 'N/A',
        "code": user.code or '',
        "recommended_by": str(user.recommended_by) or 'N/A',
        "account_type": user.account_type,
        "today_earnings": user.today_earnings,
        "country_ip": user.country_ip,
        "register_ip": user.register_ip,
        "last_login_ip": user.last_login_ip,
        "date_joined": user.date_joined,
        "last_login_country": user.last_login_country,
        "tasks_left_today": user.tasks_left_today,
        "role": user.role,
    }

    # Serialize tasks and transactions
    tasks = Task.objects.filter(user=user)
    transactions = Transaction.objects.filter(user=user)
    withdrawals = Withdrawal.objects.filter(user=user)
    task_serializer = TaskSerializer(tasks, many=True)
    transaction_serializer = TransactionSerializer(transactions, many=True)
    Withdrawal_serializer = WithdrawalSerializer(withdrawals, many=True)

    # Add tasks and transactions data to the user_data dictionary
    user_data["tasks"] = task_serializer.data
    user_data["transactions"] = transaction_serializer.data
    user_data["withdrawals"] = Withdrawal_serializer.data

    return Response(user_data, status=200)

from rest_framework.generics import GenericAPIView  # Updated this import


class UserNotificationsList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class MarkAllNotificationsAsRead(APIView):
    permission_classes = [IsAuthenticated]
    permission_classes = [IsOwnerOfNotification]

    def patch(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        
        if notifications.exists():
            notifications.update(is_read=True)
            return Response({"detail": f"r."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "re."}, status=status.HTTP_200_OK)
################################################################################################
#fetch wallet


@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
@authentication_classes([IsOwnerOfNotification])
class UnreadNotificationsCount(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get(self, request):
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": unread_notifications_count})
    
from decimal import Decimal
import copy
from django.db.models import Q

# class FetchProductView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [JWTAuthentication]

#     def get(self, request, *args, **kwargs):
#         user = get_object_or_404(CustomUser, username=self.request.user.username)

#         # Preliminary checks
#         if user.balance < 20:
#             return Response({'error_code': 'INSUFFICIENT_BALANCE'}, status=400)
#         if Task.objects.filter(user=user, status='pending').exists():
#             return Response({'error_code': 'PENDING_TASK'}, status=400)
#         if user.tasks_left_today == 0:
#             return Response({'error_code': 'NO_TASKS_LEFT'}, status=400)

#         products = self._load_products()
#         user_account_type = user.account_type.capitalize()

#         remaining_products = [product for product in products if product['account_type'] == user_account_type]
#         if not remaining_products:
#             return Response({'message': 'No products currently available. Please try again later.'}, status=400)

#         selected_product = self._select_product(user, user_account_type, remaining_products)
#         if not selected_product:
#             return Response({'message': 'No suitable product found.'}, status=400)

#         # Create task and update user attributes
#         task = Task.objects.create(
#             user=user,
#             price=selected_product['price'],
#             task_type=selected_product['title'],
#             status='pending',
#             commission_percentage=selected_product['commission_value'],
#             image=selected_product['image'],
#             commission=selected_product['commission']
#         )
#         user.pending_tasks.add(task)
#         user.save()

#         return Response({'selected_product': selected_product}, status=200)

#     def _load_products(self):
#         with open('appi/product_data/products.json', 'r') as file:
#             return json.load(file)

#     def _select_product(self, user, account_type, products):
#         completed_tasks_count = user.completed_tasks_current_cycle
#         matching_config = TaskConfiguration.objects.filter(
#             Q(user=user) | Q(user__isnull=True),
#             account_type=account_type,
#             count=completed_tasks_count
#         ).first()

#         if not matching_config:  # No unaffordable task matched
#             matching_config = TaskConfiguration.objects.filter(
#                 Q(user=user) | Q(user__isnull=True),
#                 account_type=account_type,
#                 count__isnull=True
#             ).first()
        
#         if matching_config:
#             products_in_range = [p for p in products if matching_config.price_range[0] <= p['price'] <= matching_config.price_range[1]]
            
#             if products_in_range:
#                 selected_product = random.choice(products_in_range)
#                 selected_product = copy.deepcopy(selected_product)
#                 selected_product['commission_value'] = matching_config.commission_percentage
#                 selected_product['commission'] = (selected_product['price'] * matching_config.commission_percentage) / 100
#                 return selected_product

#         return None
#     def _generate_product_data(self, config, products):
#         selected_price = Decimal(random.uniform(config.price_range_low, config.price_range_high))
#         product = random.choice(products)
#         product = copy.deepcopy(product)
#         product['price'] = selected_price
#         product['commission_value'] = config.commission_percentage
#         product['commission'] = float((selected_price * config.commission_percentage) / 100)
#         return product

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class FetchProductView(APIView):

 
    UNAFFORDABLE_TASKS = {
            "Bronze": {
                1: {"count":10, "price_range": (95, 98), "commission_percentage": 5},
                2: {"count":25, "price_range": (190, 199), "commission_percentage": 15},
                3: {"count":40, "price_range": (350, 430), "commission_percentage": 10}, 
                4: {"count":55, "price_range": (300, 330), "commission_percentage": 5}, 
            },
            "Silver": {
                1: {"count": 10, "price_range": (400, 450), "commission_percentage": 5},
                2: {"count": 29, "price_range": (900, 1200), "commission_percentage": 5},
                3: {"count": 50, "price_range": (1500, 2100), "commission_percentage": 5}
            },
            "Gold": {
                1: {"count": 23, "price_range": (3450, 3300), "commission_percentage": 5},
                2: {"count": 42, "price_range": (5401, 5999), "commission_percentage": 10},
                3: {"count": 55, "price_range": (8100, 8600), "commission_percentage": 10}
            },
            "Platinum": {
                1: {"count": 15, "price_range": (8500, 10900), "commission_percentage": 7},
                2: {"count": 30, "price_range": (20000, 22000), "commission_percentage": 7}
            },
            "Diamond": {
                1: {"count": 25, "price_range": (15000, 19500), "commission_percentage": 10},
                2: {"count": 35, "price_range": (20000, 49000), "commission_percentage": 10}
            }
        }



 #will find task, if user has not
    AFFORDABLE_TASKS = {
    "Bronze": {
        "price_range": (1.14, 4.85), 
        "commission_percentage": 15
    },
    "Silver": {
        "price_range": (60, 110), 
        "commission_percentage": 9
    },
    "Gold": {
        "price_range": (350, 499), 
        "commission_percentage": 5
    },
    "Platinum": {
        "price_range": (650, 1400), 
        "commission_percentage": 9
    },
    "Diamond": {
        "price_range": (3000, 10000), 
        "commission_percentage": 4
    },
    
}
    RANKS = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
    def get_next_rank(self, current_rank):
        try:
            current_index = self.RANKS.index(current_rank)
            # If it's not Diamond, get the next rank; else, Diamond is the highest rank, so stay there.
            return self.RANKS[current_index + 1 if current_index + 1 < len(self.RANKS) else current_index]
        except ValueError:
            raise ValueError(f"Unknown rank: {current_rank}")

    @permission_classes([IsAuthenticated])
    @authentication_classes([JWTAuthentication])
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, username=self.request.user.username)

        # Preliminary checks
        if user.balance < 20:
            return Response({'error_code': 'INSUFFICIENT_BALANCE'}, status=400)

        if Task.objects.filter(user=user, status='pending').exists():
            return Response({'error_code': 'PENDING_TASK'}, status=400)

        if user.tasks_left_today == 0:
            return Response({'error_code': 'NO_TASKS_LEFT'}, status=400)

        with open('appi/product_data/products.json', 'r') as file:
            data = json.load(file)

        user_account_type = user.account_type.capitalize()
        completed_tasks_count = user.completed_tasks_current_cycle
        
        next_rank = self.get_next_rank(user_account_type) if user_account_type != 'Diamond' else 'Diamond'
        next_rank_products = [product for product in data if product['account_type'] == next_rank]

        # Filter out products based on the user's account type
        remaining_products = [product for product in data if product['account_type'] == user_account_type]

        if not remaining_products:
            return Response({'message': 'No products currently available. Please try again later.'}, status=400)

        account_data = self.UNAFFORDABLE_TASKS.get(user_account_type)
        if not account_data:
            raise ValueError(f"Unknown account type: {user_account_type}")

        selected_product = None
        for level, task_data in sorted(account_data.items()):
            if completed_tasks_count == task_data["count"]:
                # Choose from next rank's products if available, otherwise use the remaining products from the current rank
                relevant_products = next_rank_products if next_rank_products else remaining_products

                # Randomly select a price within the given range
                selected_price = Decimal(random.uniform(*task_data['price_range']))

                # Selecting a random product within the relevant products
                selected_product = random.choice(relevant_products)
                selected_product = copy.deepcopy(selected_product)
                selected_product['price'] = selected_price
                selected_product['commission_value'] = task_data['commission_percentage']
                selected_product['commission'] = (selected_price * task_data['commission_percentage']) / 100

                user.completed_tasks_count += 1
                user.completed_tasks_current_cycle += 1
                break

        if not selected_product:
           
            affordable_data = self.AFFORDABLE_TASKS.get(user_account_type)

            # Randomly select a price within the given range
            selected_price = Decimal(random.uniform(*affordable_data['price_range']))

            # Selecting a random product within the remaining products
            selected_product = random.choice(remaining_products)
            selected_product = copy.deepcopy(selected_product)
            selected_product['price'] = selected_price
            selected_product['commission_value'] = affordable_data['commission_percentage']
            selected_product['commission'] = (selected_price * affordable_data['commission_percentage']) / 100

        # Create task and update user attributes
        task = Task.objects.create(
            user=user,
            price=selected_price,
            task_type=selected_product['title'],
            status='pending',
            commission_percentage=selected_product['commission_value'],
            image=selected_product['image'],
            commission=selected_product['commission']
        )
        user.pending_tasks.add(task)
        user.save()

        product_detail = {
            'title': selected_product['title'],
            'price': float(selected_price),
            'commission_percentage': float(selected_product['commission_value']),
            'image': selected_product['image'],
            'commission': float(selected_product['commission']),
        }

        return Response({'selected_product': product_detail}, status=200)

    # class FetchProductView(APIView):
    # # Define the constants for each account type
    # UNAFFORDABLE_TASKS_COUNT_Bronze = 5
    # UNAFFORDABLE_TASKS_PRICE_RANGE_Bronze = (80, 90)

    # # Silver constants:
    # UNAFFORDABLE_TASKS_COUNT_Silver = 10
    # UNAFFORDABLE_TASKS_PRICE_RANGE_Silver = (310, 400)
    # SECOND_UNAFFORDABLE_TASKS_COUNT_Silver = 15
    # SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Silver = (290, 600)
    # THIRD_UNAFFORDABLE_TASKS_COUNT_Silver = 20
    # SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Silver = (290, 600)

    # # Gold constants:
    # UNAFFORDABLE_TASKS_COUNT_Gold = 15
    # UNAFFORDABLE_TASKS_PRICE_RANGE_Gold = (240, 360)
    # SECOND_UNAFFORDABLE_TASKS_COUNT_Gold = 25
    # SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Gold = (400, 520)

    # # Platinum constants:
    # UNAFFORDABLE_TASKS_COUNT_Platinum = 20
    # UNAFFORDABLE_TASKS_PRICE_RANGE_Platinum = (240, 360)
    # SECOND_UNAFFORDABLE_TASKS_COUNT_Platinum = 30
    # SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Platinum = (400, 520)

    # # Diamond constants:
    # UNAFFORDABLE_TASKS_COUNT_Diamond = 25
    # UNAFFORDABLE_TASKS_PRICE_RANGE_Diamond = (240, 360)
    # SECOND_UNAFFORDABLE_TASKS_COUNT_Diamond = 35
    # SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Diamond = (400, 520)

    # @permission_classes([IsAuthenticated])
    # @authentication_classes([JWTAuthentication])
    # def get(self, request, *args, **kwargs):
    #     user = get_object_or_404(CustomUser, username=self.request.user.username)
    #     selected_product = None  # Initialize selected_product to None

    #     if user.balance < 20:
    #         return Response({'message': 'Insufficient balance to grab a task. Please recharge.'}, status=400)

    #     # Check for pending task
    #     if Task.objects.filter(user=user, status='pending').exists():
    #         return Response({'message': 'You have an existing pending task. Please complete it before grabbing a new one.'}, status=400)

    #     # Check daily tasks limit
    #     if user.tasks_left_today == 0:
    #         return Response({'message': 'You have reached your daily limit for order, Please upgrade for more daily tasks'}, status=400)

    #     with open('appi/product_data/products.json', 'r') as file:
    #         data = json.load(file)

    #     user_account_type = user.account_type.capitalize()
    #     completed_tasks_today = Task.objects.filter(user=user, status='completed', created_at__date=datetime.today().date()).count()

    #     # Exclude previously selected products
    #     previously_selected_titles = Task.objects.filter(user=user).values_list('task_type', flat=True)
        
    #     # Sort the products by price after filtering them based on the account type.
    #     remaining_products = sorted(
    #         [product for product in data if product['title'] not in previously_selected_titles and product['account_type'] == user_account_type],
    #         key=lambda x: float(x['price'])
    #     )

    #     # Define the account type specific constants
    #     if user_account_type == "Bronze":
    #         task_count_threshold = self.UNAFFORDABLE_TASKS_COUNT_Bronze
    #         price_range = self.UNAFFORDABLE_TASKS_PRICE_RANGE_Bronze

    #     elif user_account_type == "Silver":
    #         if completed_tasks_today < 2: # as Silver gets 2 tasks a day
    #             task_count_threshold = self.UNAFFORDABLE_TASKS_COUNT_Silver
    #             price_range = self.UNAFFORDABLE_TASKS_PRICE_RANGE_Silver
    #         else:
    #             task_count_threshold = self.SECOND_UNAFFORDABLE_TASKS_COUNT_Silver
    #             price_range = self.SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Silver

    #     elif user_account_type == "Gold":
    #         if completed_tasks_today < 3: # as Gold gets 3 tasks a day
    #             task_count_threshold = self.UNAFFORDABLE_TASKS_COUNT_Gold
    #             price_range = self.UNAFFORDABLE_TASKS_PRICE_RANGE_Gold
    #         else:
    #             task_count_threshold = self.SECOND_UNAFFORDABLE_TASKS_COUNT_Gold
    #             price_range = self.SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Gold

    #     elif user_account_type == "Platinum":
    #         if completed_tasks_today < 4: # as Platinum gets 4 tasks a day
    #             task_count_threshold = self.UNAFFORDABLE_TASKS_COUNT_Platinum
    #             price_range = self.UNAFFORDABLE_TASKS_PRICE_RANGE_Platinum
    #         else:
    #             task_count_threshold = self.SECOND_UNAFFORDABLE_TASKS_COUNT_Platinum
    #             price_range = self.SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Platinum

    #     elif user_account_type == "Diamond":
    #         if completed_tasks_today < 5: # as Diamond gets 5 tasks a day
    #             task_count_threshold = self.UNAFFORDABLE_TASKS_COUNT_Diamond
    #             price_range = self.UNAFFORDABLE_TASKS_PRICE_RANGE_Diamond
    #         else:
    #             task_count_threshold = self.SECOND_UNAFFORDABLE_TASKS_COUNT_Diamond
    #             price_range = self.SECOND_UNAFFORDABLE_TASKS_PRICE_RANGE_Diamond
            

    #     # Check if the user has crossed the challenge threshold
    #     if user.tasks_done_today == task_count_threshold:
    #         print("Looking for an unaffordable product...")
    #         selected_product = next((product for product in remaining_products if Decimal(product['price']) > user.balance and price_range[0] <= Decimal(product['price']) <= price_range[1]), None)
    #         if not selected_product and remaining_products:  # if we don't find such a product, fallback to fetching affordable product
    #             selected_product = remaining_products[0]  # Get the cheapest product after all the conditions.
    #     elif remaining_products:
    #         selected_product = remaining_products[0]  # Get the cheapest product after all the conditions.

    #     # Handle the case if no product is selected or the list is empty
    #     if not selected_product or not remaining_products:
    #         return Response({'message': 'No products available for your balance'}, status=400)
    #     if selected_product:
    #         print(f"Selected unaffordable product: {selected_product['title']} with price: {selected_product['price']}")
    #     else:
    #         print("No unaffordable product found. Falling back to cheapest product.")

    #     print(f"User balance: {user.balance}")
    #     print(f"User account type: {user_account_type}")
    #     print(f"Tasks completed today: {completed_tasks_today}")
            
    #     print(f"Price range for unaffordable tasks: {price_range}")
    #                 # Create task and update user attributes
    #     task = Task.objects.create(
    #         user=user,
    #         price=Decimal(selected_product['price']),
    #         task_type=selected_product['title'],
    #         status='pending',
    #         commission_percentage=float(selected_product['commission_value']),
    #         image=selected_product['image'],
    #         commission=Decimal(selected_product['commission']),
    #     )
    #     user.pending_tasks.add(task)
    #     user.tasks_left_today -= 1
    #     user.save()

    #     product_detail = {
    #         'title': selected_product['title'],
    #         'price': float(selected_product['price']),
    #         'commission_percentage': float(selected_product['commission_value']),
    #         'image': selected_product['image'],
    #         'commission': float(selected_product['commission']),
    #     }

    #     return Response({'selected_product': product_detail}, status=200)


#get everything task related to the user, gets all their tasks, completed, pending, and frozen
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class FetchUserTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        tasks = Task.objects.filter(user=user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class AdminTaskUpdateView(APIView):
    ALLOWED_STATUSES = ['completed', 'pending', 'frozen']

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        # Check the new status in request
        new_status = request.data.get('status')
        print("Received status:", new_status)  # Debugging line
        print("Allowed statuses:", self.ALLOWED_STATUSES)  # Debugging line

        if new_status not in self.ALLOWED_STATUSES:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        # If the status is "frozen", move the user's balance to "hold_balance"
        if new_status == 'frozen':
            user = task.user
            user.hold_balance += user.balance
            user.balance = Decimal('0.00')
            user.save()

        # If the status is set to "pending", reset the created_at field to the current time
        if new_status == 'pending':
            task.created_at = datetime.now()

        # Updating the task's status
        task.status = new_status
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

from django.shortcuts import get_object_or_404
from decimal import Decimal
from rest_framework import status


ALLOWED_STATUSES = ['completed', 'pending', 'frozen']

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class TaskUpdateView(APIView):
    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        # Check if the user is the owner of the task
        if task.user != request.user:
            return Response({"error": "You do not have permission to modify this task"}, status=status.HTTP_403_FORBIDDEN)

        if 'status' in request.data:
            new_status = request.data['status'].lower()
            if new_status not in ALLOWED_STATUSES:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

            old_status = task.status.lower()
            user = task.user

            # If trying to unlock a frozen task, check if user can afford the task
            if old_status == 'frozen' and new_status != 'frozen':
                if user.balance < Decimal(task.price):
                    required_deposit = Decimal(task.price) - user.balance
                    return Response({"error": f"You cannot afford to unlock this task. Required deposit: ${required_deposit}"}, status=status.HTTP_400_BAD_REQUEST)
                
            # If trying to complete a task, check for frozen tasks first
            elif new_status == 'completed':
                has_frozen_tasks = Task.objects.filter(user=user, status='frozen').exclude(pk=pk).exists()
                if has_frozen_tasks:
                    return Response({"error": "You have a frozen task. Resolve it before completing other tasks."}, status=status.HTTP_400_BAD_REQUEST)

                # Ensure user can afford the task
                if user.balance < Decimal(task.price):
                    required_deposit = Decimal(task.price) - user.balance
                    return Response({"error": f"You cannot afford to complete this task. Required deposit: ${required_deposit}"}, status=status.HTTP_400_BAD_REQUEST)

            # Update the task's status
            task.status = new_status
            task.save()

            # Task status updated to 'completed'
            if new_status == 'completed' and old_status != 'completed':
                task.completion_date = timezone.now().date()
                task.save()
                # Deduct the task's price from user's balance
                # Update user's earnings
                user.today_earnings += Decimal(task.commission)
                user.total_earnings += Decimal(task.commission)
                user.balance += Decimal(task.commission)  # Adding commission to user's balance

                # Increment tasks done today and completed tasks count
                user.tasks_done_today += 1
                user.completed_tasks_count += 1
                user.completed_tasks_current_cycle += 1 
                user.tasks_left_today -= 1

            user.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)




from django.db.models import Sum

@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class GetanalyticsView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):  # Rename this method to 'get' and add self as first parameter
    
        user = request.user

        # Check if the user is authenticated and not an instance of AnonymousUser
        if not user.is_authenticated or user.is_anonymous:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        # Get today's date
        today = timezone.now().date()

        # Calculate the date 7 days ago
        seven_days_ago = today - timedelta(days=6)  # Adjusted to include today in the 7-day range

        # Get the tasks that were completed in the last 7 days for the specific user
        tasks = Task.objects.filter(user=user, status='completed', completion_date__range=(seven_days_ago, today))

        # Annotate the sum of earnings each day
        daily_earnings_query = (
            tasks.values('completion_date')  # Group by completion date
            .annotate(total_earnings=Sum('commission'))  # Sum the commissions earned each day
            .order_by('completion_date')  # Order by completion date
        )

        # Convert query results to a dictionary for easier manipulation
        daily_earnings_dict = {item['completion_date']: item['total_earnings'] for item in daily_earnings_query}

        # Create a list to hold earnings data for each of the past 7 days
        daily_earnings = []

        for i in range(7):
            # Calculate the date for each day within the 7-day range
            current_date = seven_days_ago + timedelta(days=i)

            # Get earnings for the current date, or 0 if there is no data
            earnings = daily_earnings_dict.get(current_date, 0)

            daily_earnings.append({
                'date': current_date,
                'earnings': earnings
            })

        # Create a response dictionary
        earnings_data = {
            'user': user.username,
            'daily_earnings': daily_earnings,
        }

        return JsonResponse(earnings_data)






#allows user to request withdrawl, needs to be approved in dashboard
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
class WithdrawalListCreateView(generics.ListCreateAPIView):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer

    def create(self, request, *args, **kwargs):
        # Get the user profile
        user_profile = CustomUser.objects.get(id=request.user.id)
        
        # Check if the hold_balance is greater than zero
        if user_profile.hold_balance > 0:
            return Response({
                'error': 'You have an outstanding hold balance. '
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pending_tasks = Task.objects.filter(user=user_profile, status="pending")
        if pending_tasks.exists():
            return Response({
                'error': 'You must finish all pending tasks before withdrawing.'
            }, status=status.HTTP_400_BAD_REQUEST)

        return super(WithdrawalListCreateView, self).create(request, *args, **kwargs)


#allows user to update delivery wallet address !!!!!!!!! need double check it works
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_delivery_address(request, user_id):
    # Ensure that the user_id from the request matches the authenticated user's ID
    if request.user.id != int(user_id):
        return Response({'message': 'You are not authorized to update this address.'}, status=403)
    
    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    delivery_address = request.data.get('deliveryAddress')

    # Validate the delivery address to ensure it only contains letters and numbers
    if not re.match("^[A-Za-z0-9]+$", delivery_address):
        return Response({'error': 'Invalid wallet address format.'}, status=400)

    # Check if the user is updating too frequently
    now = timezone.now()
    if user.last_address_update and (now - user.last_address_update) < timedelta(days=1):
        return Response({'message': 'You can only update your delivery address once every 24 hours.'}, status=400)

    # Construct data for the serializer
    address_data = {'deliveryAddress': delivery_address} 

    serializer = UserSerializer(user, data=address_data, partial=True)
    if serializer.is_valid():
        user.last_address_update = now  # Update the timestamp when the address is changed
        user.save()  # Save the timestamp
        serializer.save()
        return Response(serializer.data, status=200)

    return Response(serializer.errors, status=400)
    



#this is used to fetch user data when updatebalance is called from the main authcontext.jsx, need to double check this is safe!!!!!!
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_user_data(request):
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'balance': request.user.balance,  # Replace 'balance' with the actual field name in your CustomUser model
        'hold_balance': request.user.hold_balance,  # Added the completed_tasks_count field
        'code': request.user.code,  # Replace 'balance' with the actual field name in your CustomUser model
        'account_type': request.user.account_type,  # Replace 'balance' with the actual field name in your CustomUser model
        'deliveryAddress': request.user.deliveryAddress,  # Replace 'balance' with the actual field name in your CustomUser model
        'today_earnings': request.user.today_earnings,  # Replace 'balance' with the actual field name in your CustomUser model
        'total_earnings': request.user.total_earnings,  # Replace 'balance' with the actual field name in your CustomUser model
        'completed_tasks_count': request.user.completed_tasks_count,  # Added the completed_tasks_count field
        'tasks_left_today': request.user.tasks_left_today,  # Added the completed_tasks_count field
        'tasks_done_today': request.user.tasks_done_today,  # Added the completed_tasks_count field
        # Add other fields you want to include in the user data response
    }

    return Response(user_data)

#gets withdrawal and deposit history of the user
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class UserActivityView(APIView):
    def get(self, request):
        # Get approved transactions
        transactions = Transaction.objects.filter(user=request.user, status=Transaction.STATUS_APPROVED)
        transaction_serializer = TransactionSerializer(transactions, many=True)

        # Get approved withdrawals
        withdrawals = Withdrawal.objects.filter(user=request.user, status=Withdrawal.STATUS_APPROVED)
        withdrawal_serializer = WithdrawalSerializer(withdrawals, many=True)

        return Response({
            'transactions': transaction_serializer.data,
            'withdrawals': withdrawal_serializer.data,
        })
    


from PIL import Image as PILImage
from django.core.validators import FileExtensionValidator
import io

#uploads image file of user deposit , the above TransactionDetail fethces the data here
@authentication_classes([JWTAuthentication])
class FileUploadView(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        image = request.FILES.get('file')
        user_id = request.data.get('user')

        if not all([amount, image, user_id]):
            return Response(
                {'detail': 'Please make sure you have chosen a correct amount an appropiate screenshot'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate the amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValidationError("Invalid amount.")
        except ValueError:
            raise ValidationError("Invalid amount.")

        # Validate the image extension using Django's validator
        validator = FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])
        validator(image)

        # Validate the image's content type
        allowed_content_types = ['image/png', 'image/jpeg']
        content_type = image.content_type
        if content_type not in allowed_content_types:
            return Response(
                {'detail': 'Invalid file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Limit the image size (e.g., 5 MB)
        max_image_size_bytes = 5 * 1024 * 1024  # 5 MB
        if image.size > max_image_size_bytes:
            return Response(
                {'detail': 'error uploading file, Please contact Cusomter Service.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Try to open and re-save the image to ensure it's valid and to strip metadata
        try:
            img = PILImage.open(image)
            buffer = io.BytesIO()
            img_format = 'JPEG' if content_type == 'image/jpeg' else 'PNG'
            img.save(buffer, format=img_format)
            
            # Renaming the file here before saving it
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            file_extension = 'jpg' if content_type == 'image/jpeg' else 'png'
            new_file_name = f"user_{user_id}_transaction_{current_time}.{file_extension}"
            image.name = new_file_name
            
            image.file = buffer
        except Exception as e:
            return Response(
                {'detail': f'Error uploading file, Please contact Customer Service.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File validation and user permission checks are completed
        # Create the transaction object
        user = get_object_or_404(CustomUser, id=user_id)
        transaction = Transaction.objects.create(
            amount=amount,
            image=image,
            user_id=user_id
        )
        send_telegram_notification = TelegramNotificationConfig.objects.first().send_telegram_notification

        # send_telegram_notification = False 
        if send_telegram_notification:
            try:
                # Make sure the buffer pointer is at the beginning
                buffer.seek(0)
                image_data = buffer.getvalue()  # Get the image data from the buffer

                full_name = f"{user.first_name} {user.last_name}"
            
                message = (
                    f"🔔 New Transaction Alert! 🔔\n"
                    f"-----------------------------------\n"
                    f"👤 Username: {user.username}\n"
                    f"📛 Name: {full_name}\n"
                    f"🏠 Delivery Address: {user.deliveryAddress}\n"
                    f"💼 Account Type: {user.account_type}\n"
                    f"🤝 Recommended By: {user.recommended_by}\n"
                    f"💰 Amount: ${amount:.2f}\n"
                    f"-----------------------------------\n"
                    f"📌 Please review the attached image for details."
                )
                telegram_api_url = f"https://api.telegram.org/bot6643987063:AAGlRNfdQjP_hScHy26utBuqfcUQ-6AH_g8/sendPhoto"
                image_file = {'photo': (new_file_name, image_data, content_type)}

                params = {
                    "chat_id": -4028489314,  # Use the group chat ID
                    "caption": message,
                }

                # Send the POST request to Telegram
                response = requests.post(telegram_api_url, files=image_file, data=params)
                response_data = response.json()

                if not response_data.get("ok"):
                    raise Exception(response_data.get("description"))

            except Exception as e:
                print(f"Error sending message to Telegram group: {str(e)}")


        return Response(
            TransactionSerializer(transaction, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
# telegram_api_url = f"https://api.telegram.org/bot6643987063:AAGlRNfdQjP_hScHy26utBuqfcUQ-6AH_g8/sendPhoto"

#######admin/housekeeping views###############################################################################################################

@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def get_user_by_username(request, username):
    try:
        user = CustomUser.objects.get(username=username)
        return JsonResponse({"id": user.id, "username": user.username})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    

@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def hr_manage_withdrawal(request, withdrawal_id):
    try:
        withdrawal = Withdrawal.objects.get(pk=withdrawal_id)
    except Withdrawal.DoesNotExist:
        return Response({"error": "Withdrawal not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = WithdrawalSerializer(withdrawal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#gets all registered users data, need to add permission classes to only allows housekeeping and admin
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


    def referral_link(self, request, *args, **kwargs):
        user = self.get_object()
        referral_link = request.build_absolute_uri(f'/register?ref={user.code}')
        return Response({'referral_link': referral_link}, status=status.HTTP_200_OK)
    

@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class InvitedUsersViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        # Assuming 'code' is a unique identifier for each user
        return CustomUser.objects.filter(recommended_by=user)
    

@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class BanUserView(APIView):
    permission_classes = [IsHousekeepingOrHR, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'No reason provided.')
        # Log the ban event, optionally you can use the Python logging module or save it to a model
        print(f"User {user.username} (ID: {user.id}) banned. Reason: {reason}")

        user.delete()

        return Response({"detail": "User banned and all related data deleted."}, status=status.HTTP_200_OK)

@permission_classes([IsHR]) 
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class Togtelegram(APIView):
    def get(self, request):
        try:
            config = TelegramNotificationConfig.objects.get(pk=1)
            return Response({'success': True, 'current_status': config.send_telegram_notification})
        except TelegramNotificationConfig.DoesNotExist:
            return Response({'success': False, 'error': 'Configuration not found.'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)})

    def post(self, request):
        try:
            config = TelegramNotificationConfig.objects.get(pk=1)
            # Get the current status before toggling
            current_status = config.send_telegram_notification
            # Toggle the current value
            config.send_telegram_notification = not current_status
            
            # Get the username of the user who made the request
            username = request.user.username  # Assuming the user is authenticated
            
            config.save()
            
            # Send a request to the Telegram Bot API to notify the group
            chat_id = '-4028489314'
            action = "turned off" if current_status else "turned on"
            message = f'{username} has {action} notifications.'
            telegram_api_url = f"https://api.telegram.org/bot6643987063:AAGlRNfdQjP_hScHy26utBuqfcUQ-6AH_g8/sendMessage"
            data = {'chat_id': chat_id, 'text': message}
            response = requests.post(telegram_api_url, data=data)
            
            return Response({'success': True, 'current_status': config.send_telegram_notification})
        except TelegramNotificationConfig.DoesNotExist:
            return Response({'success': False, 'error': 'Configuration not found.'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)})
    



@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def reset_user(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)

        # Reset user fields
        user.tasks_done_today = 0
        user.tasks_left_today = 60  # Adjust this value as per the business logic
        user.today_earnings = 0
        user.total_earnings = 0
        user.completed_tasks_count = 0
        user.completed_tasks_current_cycle = 0
        user.balance = 0.00
        user.hold_balance = 0.00
        user.account_type = 'bronze'  # Set to default account type
        user.save()

        # Reset user tasks
        Task.objects.filter(user=user).delete()

        # Reset transactions
        Transaction.objects.filter(user=user).delete()

        # Reset withdrawals
        Withdrawal.objects.filter(user=user).delete()

        # Reset notifications
        Notification.objects.filter(user=user).delete()

        return JsonResponse({'status': 'success', 'message': 'User info and related data have been reset.'})

    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    


@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class HoldBalanceView(APIView):
    permission_classes = [IsHousekeepingOrHR, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Transfer all of user's balance to hold_balance
        user.hold_balance += user.balance
        user.balance = 0
        user.save()

        # Optionally, you can log the action.
        print(f"Transferred balance to hold for user {user.username} (ID: {user.id})")

        return Response({"detail": f"User {user.username}'s balance transferred to hold."}, status=status.HTTP_200_OK)
    

@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class ChangeAccountTypeView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingOrHR]
    authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        new_account_type = request.data.get("new_account_type")

        # Perform validation on the new account type if needed
        # For example, check if the new account type is valid

        user.account_type = new_account_type
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])   
class ReleaseHoldBalanceView(APIView):
    permission_classes = [IsHousekeepingOrHR, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Transfer all of user's hold_balance back to balance
        user.balance += user.hold_balance
        user.hold_balance = 0
        user.save()

        # Optionally, you can log the action.
        print(f"Released hold balance for user {user.username} (ID: {user.id})")

        return Response({"detail": f"User {user.username}'s hold balance released back to main balance."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def send_notification(request):
    user_id = request.data.get('user')
    try:
        user_instance = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=404)

    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user_instance)
        return Response({'detail': 'Notification sent successfully.'}, status=201)
    return Response(serializer.errors, status=400)


#gets withdrawal data
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class WithdrawalDetail(generics.RetrieveUpdateAPIView):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        withdrawal = self.get_object()
        print(f"Starting the withdrawal process for user: {withdrawal.user.id}, amount: {withdrawal.amount}, current balance: {withdrawal.user.balance}")

        # Initialize the serializer with the current withdrawal data
        serializer = self.get_serializer(withdrawal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        notification_title = ""
        notification_content = ""
        notification_type = "info"

        # Check if the status is changed to "approved"
        if request.data.get('status') == 'approved':

            # Ensure the same withdrawal request can't be approved more than once
            if withdrawal.status == 'approved':
                raise ValidationError("This withdrawal request has already been approved.")

            # Deduct the withdrawn amount from the user's balance

            # Explicitly update and save the withdrawal's status
            withdrawal.status = 'approved'
            withdrawal.save()

            # Save the user's updated balance
            withdrawal.user.save()

            # Set up the notification details for successful withdrawal
            notification_title = "WithdrawalApproved"
            notification_content = f"Your withdrawal of {withdrawal.amount} has been approved."
            notification_type = "success"

        else:
            # If the status is not "approved", then use the serializer's regular update
            self.perform_update(serializer)

            # Set up the notification details for failed withdrawal
            notification_title = "WithdrawalDenied"
            notification_content = "Your withdrawal request has been denied. Please check the details and try again."
            notification_type = "warning"

        # Create a notification for the user
        Notification.objects.create(
            user=withdrawal.user, 
            title=notification_title, 
            content=notification_content, 
            type=notification_type
        )

        print(f"After deducting amount for user: {withdrawal.user.id}, new balance: {withdrawal.user.balance}")
        return Response(serializer.data, status=status.HTTP_200_OK)
        

#gets deposit data
@permission_classes([IsHousekeepingOrHR])  # Use IsHR if only HR should have access, or IsHousekeepingOrHR if housekeeping should also have access
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
class TransactionList(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

@permission_classes([IsAuthenticated, IsHousekeepingOrHR])
@authentication_classes([JWTAuthentication])
class InvitedUsersTransactionsList(generics.ListAPIView):
    serializer_class = TransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsHousekeepingOrHR]

    def get_queryset(self):
        # Get the current logged-in user
        user = self.request.user

        # Get all users invited by the logged-in user
        invited_users = CustomUser.objects.filter(recommended_by=user)

        # Now, get all transactions related to the invited users
        invited_users_transactions = Transaction.objects.filter(user__in=invited_users)
        return invited_users_transactions

    def get_serializer_context(self):
        return {'request': self.request}
    
from django.core.exceptions import ObjectDoesNotExist
import mimetypes

from rest_framework.exceptions import PermissionDenied

#alows to review transactions and approve them

@permission_classes([IsAuthenticated, IsHousekeepingOrHR])  # Combined permission_classes
@authentication_classes([JWTAuthentication])
class TransactionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


    @staticmethod
    def get_account_type(amount, current_account_type):
        account_hierarchy = ['bronze', 'silver', 'gold', 'platinum', 'diamond']

        # Determine the new account type based solely on transaction amount.
        if 20 <= amount < 100:
            prospective_account_type = 'bronze'
        elif 100 <= amount < 500:
            prospective_account_type = 'silver'
        elif 500 <= amount < 2000:
            prospective_account_type = 'gold'
        elif 2000 <= amount < 10000:
            prospective_account_type = 'platinum'
        elif amount >= 10000:
            prospective_account_type = 'diamond'
        else:
            prospective_account_type = 'bronze'

        # Compare the current and prospective account types and return the higher one.
        if account_hierarchy.index(prospective_account_type) > account_hierarchy.index(current_account_type):
            return prospective_account_type
        else:
            return current_account_type

        



    def adjust_tasks_for_upgrade(self, user):
        """Adjusts the tasks_left_today attribute for a user based on their account type."""
        if user.account_type == 'bronze':
            user.tasks_left_today = 60
        elif user.account_type == 'silver':
            user.tasks_left_today = 80
        elif user.account_type == 'gold':
            user.tasks_left_today = 120
        elif user.account_type == 'platinum':
            user.tasks_left_today = 160
        elif user.account_type == 'diamond':
            user.tasks_left_today = 200

        
        user.save()

    

       

    def perform_update(self, serializer):
        transaction = self.get_object()
        user = self.request.user
        if transaction.user.recommended_by != user and user.role != 'hr':
            # If not, raise a permission denied exception
            raise PermissionDenied('You do not have permission to modify this transaction.')


        instance = serializer.save()  # This saves the transaction object and returns the updated instance

        # Store the user's current account type
        current_account_type = instance.user.account_type

        
        # Determine new account type based on the transaction amount
        new_account_type = self.get_account_type(instance.amount, current_account_type)

        # Check if the user's current account type matches the new account type
        if current_account_type != new_account_type:
            instance.user.account_type = new_account_type
            instance.user.save()  # Save the updated account type
            instance.user.completed_tasks_current_cycle = 0
            
            # Adjust the tasks_left_today based on the new account type
            self.adjust_tasks_for_upgrade(instance.user)

        # Notification logic after updating the transaction object
        notification_title = ""
        notification_content = ""
        notification_type = "info"

        if instance.status == 'approved':
          

            notification_title = 'Transaction Approved'
            notification_content = f'Your transaction of {instance.amount} has been approved.'
            notification_type = 'success'
        elif instance.status == 'denied':
            notification_title = 'Transaction Denied'
            notification_content = f'Your transaction of {instance.amount} has been denied.'
            notification_type = 'warning'

        # Create a notification for the user
        Notification.objects.create(
            user=instance.user,
            title=notification_title,
            content=notification_content,
            type=notification_type
        )

        performed_by_user = self.request.user
        performed_by_name = f"{performed_by_user.username} {performed_by_user.role}"

        files = None

        send_telegram_notification = TelegramNotificationConfig.objects.first().send_telegram_notification

        # send_telegram_notification = False
        if send_telegram_notification:
            try:
                if hasattr(instance, 'image') and instance.image:
                    image_path = instance.image.path
                    content_type, _ = mimetypes.guess_type(image_path)

                    with open(image_path, 'rb') as image_file:
                        files = {"photo": (instance.image.name, image_file, content_type)}
                        caption = (
                            f"🔔 Transaction Update 🔔\n"
                            f"-----------------------------------\n"
                            f"👤 User: {instance.user.username}\n"
                            f"💰 Amount: ${instance.amount:.2f}\n"
                            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"🚦 Status: {'Approved ✅' if instance.status == 'approved' else 'Denied ❌'}\n"
                            f"👮‍♂️ Action by: {performed_by_name}\n"
                            f"-----------------------------------\n"
                        )

                        telegram_api_url = f"https://api.telegram.org/bot6643987063:AAGlRNfdQjP_hScHy26utBuqfcUQ-6AH_g8/sendPhoto"
                        data = {
                            "chat_id": -4028489314,  # Replace with your actual group chat ID
                            "caption": caption,
                        }

                        # Send the POST request to Telegram
                        response = requests.post(telegram_api_url, data=data, files=files)
                        response_data = response.json()

                        if not response_data.get("ok"):
                            raise Exception(response_data.get("description"))
                else:
                    raise ObjectDoesNotExist("No image found for the transaction.")
            
            except ObjectDoesNotExist as e:
                print(f"Object not found: {str(e)}")
            except Exception as e:
                print(f"Error sending message to Telegram group: {str(e)}")
        
        return super(TransactionDetail, self).perform_update(serializer)





from PIL import Image



import pandas as pd
from django.http import FileResponse
from django.conf import settings

import zipfile
from io import BytesIO
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsHR])
def download_transactions(request):
    # Create a buffer to hold the ZIP file in memory
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        # Create a Pandas DataFrame to hold transaction data
        data = pd.DataFrame(list(Transaction.objects.values()))

        # Add a new column with the image URLs or paths
        data['image_url'] = data.apply(lambda row: os.path.join('images', os.path.basename(row['image'])), axis=1)

        # Create a CSV file from the DataFrame
        csv_buffer = data.to_csv(index=False)

        # Add the CSV file to the ZIP file
        zip_file.writestr('transactions.csv', csv_buffer)

        # Add images to the ZIP file
        for transaction in Transaction.objects.all():
            image_path = os.path.join(settings.MEDIA_ROOT, str(transaction.image))  # Corrected MEDIA_ROOT
            zip_file.write(image_path, f'images/{os.path.basename(image_path)}')

    # Prepare the ZIP file response
    zip_buffer.seek(0)
    response = FileResponse(zip_buffer, as_attachment=True,
                            filename=f'transactions-{timezone.now().date()}.zip')

    return response
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsHR])
@csrf_exempt
@require_http_methods(["POST"])  
def delete_transaction_image(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)

        # If using ImageField or FileField in the model, Django provides a delete method
        if transaction.image:
            print("File path:", transaction.image.path)  # Print the path for debug
            transaction.image.delete(save=True)  # This will also set image field to None
            return JsonResponse({'message': 'Image deleted successfully'}, status=200)

        return JsonResponse({'error': 'No image found for this transaction'}, status=404)

    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        print("Exception:", e)  # Print exception for debug
        return JsonResponse({'error': str(e)}, status=500)





@api_view(["POST"])
@permission_classes([IsAuthenticated, IsHR])  # Ensure the user is authenticated and is an HR
def make_user_housekeeping(request, user_id):
    new_role = request.data.get('new_role')  # Get the new role from the request data

    # Ensure the new role is either 'user' or 'housekeeping'
    if new_role not in ['user', 'housekeeping']:
        return JsonResponse({'error': 'Invalid role assignment'}, status=400)

    try:
        user = CustomUser.objects.get(id=user_id)

        # If the new role is 'housekeeping', ensure the current role is not 'hr'
        if new_role == 'housekeeping' and user.role == 'hr':
            return JsonResponse({'error': 'Cannot change HR to housekeeping'}, status=403)
        
        user.role = new_role  # Assign the new role
        user.save()
        return JsonResponse({'message': f'User role updated to {new_role} successfully'}, status=200)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
#######housekeeping######


#######admin######











############################################












from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class RegisterViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def is_valid_phone_number(self, phone):
    # Check if phone number only contains numbers and optionally starts with '+'
        if not re.match(r'^\+?[0-9]+$', phone):
            return False

        # Check if phone number starts with '+' and has a length between 10 and 15
        if not phone.startswith('+') or not (10 <= len(phone) <= 15):
            return False

        return True

    def send_welcome_notification(self, user):
        """
        Sends a welcome notification to a newly registered user.
        """
        title = "Welcome to Our Platform!"
        content = "We're excited to have you on board. Explore and enjoy our features."
        type = "info"  # Assuming you have a 'type' field in Notification model

        # Create a notification (this assumes you have a Notification model with these fields)
        Notification.objects.create(user=user, title=title, content=content, type=type)

    def create(self, request, *args, **kwargs):
        ref_code = request.data.get('ref_code')

        # Check if the referral code is provided and exists
        if ref_code:
            referred_by = CustomUser.objects.filter(code=ref_code).first()
            if not referred_by:
                return Response({'detail': 'Invalid referral code provided!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            referred_by = None

        code = generate_ref_code()  # Generate a new code
        request.data['code'] = code  # Set the generated code in the request data

        # Validate and sanitize email
        email = request.data.get('email', '').strip()
        try:
            validate_email(email)
        except ValidationError:
            return Response({'detail': 'Invalid email address provided!'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and sanitize phone number
        phone = request.data.get('username', '').strip()  # Replace 'username' with the actual key for phone number
        if not self.is_valid_phone_number(phone):
            return Response({'detail': 'Invalid phone number provided!'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and sanitize password
        password = request.data.get('password', '').strip()
        if not password:
            return Response({'detail': 'Password is required!'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and sanitize referral code
        if not ref_code:
            return Response({'detail': 'Referral code is required!'}, status=status.HTTP_400_BAD_REQUEST)
        
        phone = request.data.get('username', '').strip()  # Replace 'username' with the actual key for phone number if different
        if not self.is_valid_phone_number(phone):
            return Response({'detail': 'Invalid phone number provided! Phone number must only contain numbers.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if referred_by:
            user.recommended_by = referred_by

        if 'password' in request.data:
            user.password = make_password(request.data['password'])  # Hash the password

        # You can access the client's IP address from the request object directly
        user.register_ip = request.data.get('register_ip')


        user.save()
        self.send_welcome_notification(user)
        response_data = serializer.data
        response_data['recommended_by'] = user.recommended_by_id  # Add recommended_by field to the response data

        headers = self.get_success_headers(response_data)

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

       




@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh',
    ]

    4053


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['balance'] = str(user.balance) # Convert Decimal to string
        token['code'] = user.code
        token['deliveryAddress'] = user.deliveryAddress
        token['today_earnings'] = str(user.today_earnings)  # Convert Decimal to string
        token['total_earnings'] = str(user.total_earnings)  # Convert Decimal to string
        token['role'] = user.role
        # ...

        return token
    
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import JsonResponse

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        captcha_key = request.data.get('captcha_key')
        captcha_response = request.data.get('captcha_response')

        # Verify CAPTCHA
        try:
            captcha_value = CaptchaStore.objects.get(hashkey=captcha_key).response
        except CaptchaStore.DoesNotExist:
            return JsonResponse({'detail': 'Invalid CAPTCHA'}, status=400)

        if captcha_response.lower() != captcha_value.lower():
            return JsonResponse({'detail': 'Invalid CAPTCHA'}, status=400)

        login_ip = request.data.get('login_ip')

        # Fetch the country for the IP using extreme-ip-lookup.com
        try:
            ip_info_res = requests.get(f'https://ipinfo.io/{login_ip}/json')
            ip_data = ip_info_res.json()
            login_country = ip_data.get('country', '')
        except Exception as e:
            print(f"Error fetching country for IP {login_ip}: {e}")
            login_country = ''

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.user
        user.last_login_ip = login_ip  # Update the last login IP
        user.last_login_country = login_country  # Update the last login country
        user.reset_daily_tasks() 
        user.save()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

from rest_framework_simplejwt.tokens import RefreshToken

class AdminLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            # Create a new access token with custom claims
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token['role'] = user.role  # Add the user's role to the token payload

            response.data['access'] = str(access_token)

            if user.role not in ['hr', 'housekeeping']:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)

        return response
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role(request):
    user = request.user  # The logged-in user
    role = user.role
    return Response({'role': role})

def get_captcha(request):
    captcha_key = CaptchaStore.generate_key()
    captcha_image = captcha_image_url(captcha_key)
    return JsonResponse({'captcha_key': captcha_key, 'captcha_image': captcha_image})

from django.views.decorators.http import require_http_methods


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated, IsHR])  # Use IsHR permission class
def clear_captchas(request):
    try:
        # Logic to clear expired captchas
        CaptchaStore.objects.filter(expiration__lt=timezone.now()).delete()
        
        return JsonResponse({"status": "success", "message": "Expired captchas cleared!"})
    except Exception as e:
        return JsonResponse({"detail": "Error occurred while clearing captchas.", "error": str(e)}, status=500)
