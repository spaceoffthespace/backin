from django.urls import path, include,  re_path
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.views import LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'upload', FileUploadView, basename='upload')  # Add this line
router.register(r'invited-users', InvitedUsersViewSet, basename='invi')




urlpatterns = [
    path('', include(router.urls)),
    path('register/<str:ref_code>/', RegisterViewSet.as_view({'post': 'register'}), name='register_with_ref_code'),



    #adming urls

    
    path('ban-user/', BanUserView.as_view(), name='ban_user'),
    path('reset-user/<int:user_id>/', reset_user, name='reset_user'),


    #housekeeping urls


    ######################### adming + housekeeping ############################################
    path('admin-token/', AdminLoginView.as_view(), name='admin_token_obtain_pair'),
    path('get-user-role/', get_user_role, name='get_user_role'),

    path('users-data/<int:user_id>/', user_detail, name='user-detail'),

    path('withdrawals/<int:pk>/', WithdrawalDetail.as_view()),
   
    path('toggle_telegram_notification/', Togtelegram.as_view(), name='toggle_telegram_notification'),
   
    path('transactions/<int:pk>/', TransactionDetail.as_view()),
    path('transactions/', TransactionList.as_view()),

    path('invited-users-transactions/', InvitedUsersTransactionsList.as_view(), name='invited-users-transactions'),


    path('withdrawal-update/', hr_manage_withdrawal, name='update-withdrawal'),

    path('un-tasks/<int:pk>/', AdminTaskUpdateView.as_view(), name='staff_task_update'),

    path('get-user-by-username/<str:username>/', get_user_by_username, name='get_user_by_username'),

    path('send_notification/', send_notification, name='send_notification'),

    path('hold-balance/', HoldBalanceView.as_view(), name='hold_balance'),
    path('change-account-type/<int:user_id>/', ChangeAccountTypeView.as_view(), name='change_account_type'),
    path('change-user-balance/<int:user_id>/', ChangeUserBalanceView.as_view(), name='change-user-balance'),

    path('off-t/', ToggleUnaffordableTasksView.as_view(), name='release_hold_balance'),
    path('release-hold-balance/', ReleaseHoldBalanceView.as_view(), name='release_hold_balance'),
    path('make-user-housekeeping/<int:user_id>/', make_user_housekeeping, name='make-user-housekeeping'),
    path('clear-captchas/', clear_captchas, name='clear_captchas'), 

    path('download-tran/', download_transactions, name='download_dat'), 
    path('delete-image/<int:transaction_id>/', delete_transaction_image, name='delete_image'),
      # Add this line    ########################## user urls #############################

    path('get_user_data/', get_user_data, name='get_user_data'),
    


    path('grab_order/', FetchProductView.as_view(), name='fetch_product'),
    
    path('notifications/', UserNotificationsList.as_view(), name='user-notifications'),
    path('notifications/mar/', MarkAllNotificationsAsRead.as_view(), name='mark-notification-as-read'),
    path('notifications/unr/', UnreadNotificationsCount.as_view(), name='unread-notifications-count'),

    path('activity/', UserActivityView.as_view(), name='activity'),
    path('anal/', GetanalyticsView.as_view(), name='get_daily_earnings'),
    path('requested-withdraw/', WithdrawalListCreateView.as_view(), name='withdrawals'),

    path('us-tasks/', FetchUserTasks.as_view(), name='fetch_user_tasks'),
    path('us-tasks/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),

    



    path('create-demo-account/<int:user_id>/', create_demo_account, name='create_demo_account'),            


    path('update-delivery-address/<int:user_id>/', update_delivery_address, name='update_delivery_address'),
               
    
    
    
    
    #auth
    
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('captcha/', include('captcha.urls')),
    path('get-captcha/', get_captcha, name='get_captcha'),

    # path('transactions/<int:pk>/update_status/', update_transaction_status, name='update_transaction_status'),
    # path('api/transactions/<int:pk>/approve/', approve_payment, name='approve-payment'),
    # path('api/transactions/<int:pk>/approve-withdraw/', approve_withdrawal, name='approve-withdraw'),







    # Removed the upload path here, it's now handled by the router
    # other routes here...
]