from django.conf import settings
from django.conf.urls.static import static
from tempfile import template
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from app.views import NotificationsView
from app.views import add_comment
from .views import update_comment, delete_comment
from . import views
from django.views.generic.base import RedirectView
from app.views import delete_conversation
from .views import (
    register,
    login_view,
    HomeRedirectView,
    CommissionCreateView,
    CommissionListView,
    CommissionDetailView,
    CommissionUpdateView,
    CommissionDeleteView,
    avail_commission,
)
urlpatterns = [
    path('dashboard/', views.redirect_dashboard, name='dashboard'),
    path('', views.HomeRedirectView.as_view(), name='home'),
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('commissioner/dashboard/', views.commissioner_dashboard, name='commissioner-dashboard'),
    # CRUD paths for the Commission table
    path('commissions/',CommissionListView.as_view(), name='commission-list'),
    path('commissions/create/', CommissionCreateView.as_view(), name='commission-create'),
    path('commissions/<int:pk>/', CommissionDetailView.as_view(), name='commission-detail'),
    path('commission/<int:pk>/avail/', avail_commission, name='avail-commission'),
    path('commissions/<int:pk>/update/', CommissionUpdateView.as_view(), name='commission-update'),
    path('commissions/<int:pk>/delete/', CommissionDeleteView.as_view(), name='commission-delete'),
    # crud for comment
    path('commission/<int:pk>/add-comment/', add_comment, name='add-comment'),
    path('comment/<int:pk>/edit/', update_comment, name='update-comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete-comment'),

    path('commissioner/profile/<int:pk>/', views.commissioner_profile_view, name='commissioner-profile'),
    path('send-message/<int:recipient_pk>/', views.send_message_view, name='send-message'),
    path('commissioner/inbox/', views.commissioner_inbox, name='commissioner-inbox'),
    path('student/inbox/', views.student_inbox, name='student-inbox'),
    path('message/reply/<int:recipient_pk>/', views.reply_message, name='reply-message'),
    path('conversation/<int:sender_pk>/', views.conversation_view, name='conversation'),
    path('student/conversation/<int:recipient_pk>/', views.student_conversation_view, name='student-conversation'),

    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_update, name='edit_profile'),
    path('profile/delete-picture/', views.delete_profile_picture, name='profile_picture_delete'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('commissions/save/<int:commission_id>/', views.save_commission, name='save_commission'),
    path('commissions/unsave/<int:commission_id>/', views.unsave_commission, name='unsave_commission'),
    path('commissions/saved/', views.saved_commissions, name='saved-commissions'),
    # Password reset URLs
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='app/passreset/password_reset.html'),name='password_reset'),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(template_name='app/passreset/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='app/passreset/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset_done/',auth_views.PasswordResetCompleteView.as_view(template_name='app/passreset/password_reset_complete.html'),name='password_reset_complete'),
    path('delete-conversation/<int:user_pk>/', delete_conversation, name='delete-conversation'),


    path('favicon.ico',RedirectView.as_view(url='/static/images/favicon.ico'))
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)