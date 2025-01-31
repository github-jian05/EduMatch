from django.http import JsonResponse
import os
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Q, Prefetch
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm
)
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from app.models import (
    CustomUser as User,
    Profile,
    Commission,
    Request,
    Comment,
    Message,
    Notification,
    Student
)
from .forms import (
    CommissionForm,
    UserRegistrationForm,
    ProfileUpdateForm,
    UserUpdateForm,
    RoleUpdateForm
)


@login_required
def redirect_dashboard(request):

    if request.user.is_commissioner():
        return redirect('commissioner-dashboard')
    elif request.user.is_student():
        return redirect('student-dashboard')
    else:
        messages.error(request, "You don't have the correct permissions.")
        return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user, role=role)
            else:
                user.role = role
                user.profile.save()

            login(request, user)

            messages.success(request, "Registration successful! Welcome, {}!".format(user.username))

            if role == 'student':
                return redirect('student-dashboard')
            elif role == 'commissioner':
                return redirect('commissioner-dashboard')
            else:
                messages.error(request, "Invalid role selection.")
                return redirect('register')
    else:
        form = UserRegistrationForm()

    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(request, f"Welcome back, {user.username}! You have successfully logged in.")

            if user.is_student():
                return redirect('student-dashboard')
            elif user.is_commissioner():
                return redirect('commissioner-dashboard')
            else:
                messages.warning(request, "Your role is not recognized!")
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
    else:
        form = AuthenticationForm()

    return render(request, 'app/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'app/profile.html', {
        'user': request.user,
        'profile': request.user.profile,
    })

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('some_error_page')

    commissions = Commission.objects.all()

    context = {
        'title': 'Student Dashboard',
        'student_name': request.user.first_name,
        'commissions': commissions,
    }

    return render(request, 'app/student/student_dashboard.html', context)

@login_required
def commissioner_dashboard(request):

    if request.user.role != 'commissioner':
        return redirect('some_error_page')

    commissions = Commission.objects.filter(commissioner=request.user)

    total_commissions = commissions.count()
    total_earnings = commissions.aggregate(total=models.Sum('price'))['total'] or 0

    context = {
        'title': 'Commissioner Dashboard',
        'commissioner_name': request.user.first_name,
        'commissions': commissions,
        'total_commissions': total_commissions,
        'total_earnings': total_earnings,
    }

    return render(request, 'app/commissioner/commissioner_dashboard.html', context)

@login_required
def commissioner_profile_view(request, pk):
    commissioner = get_object_or_404(Profile, user__pk=pk)

    if not commissioner.user.is_commissioner():
        return HttpResponseForbidden('The requested profile does not belong to a commissioner.')
    context = {
        'profile': commissioner,
    }
    return render(request, 'app/commissioner/commissioner_profile.html', context)

@login_required
def profile_update(request):
    profile = request.user.profile
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        role_form = RoleUpdateForm(request.POST, instance=user)

        if profile_form.is_valid() and role_form.is_valid():
            profile_form.save()
            role_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')

    else:
        profile_form = ProfileUpdateForm(instance=profile)
        role_form = RoleUpdateForm(instance=user)

    return render(request, 'app/profile_update.html', {
        'profile_form': profile_form,
        'role_form': role_form,
    })


def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')

    return render(request, 'app/delete_account.html')

def delete_profile_picture(request):
    profile = request.user.profile
    if profile.profile_picture and profile.profile_picture.name != 'profile_pictures/default.jpg':
        profile.profile_picture.delete()
        profile.profile_picture = 'profile_pictures/default.jpg'
        profile.save()
        messages.success(request, 'Your profile picture has been deleted.')
    else:
        messages.error(request, 'No custom profile picture to delete.')

    return redirect('profile')

class HomeRedirectView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return redirect('login')

class CommissionListView(LoginRequiredMixin, ListView):
    model = Commission
    template_name = 'app/commission_list.html'
    context_object_name = 'commissions'

    def get_queryset(self):
        queryset = Commission.objects.filter(available=True)

        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_dashboard_url = reverse('home')
        if hasattr(self.request.user, 'profile'):
            if self.request.user.role == 'commissioner':
                user_dashboard_url = reverse('commissioner-dashboard')
            elif self.request.user.role == 'student':
                user_dashboard_url = reverse('student-dashboard')

        context['search_query'] = self.request.GET.get('search', '')

        context['user_dashboard_url'] = user_dashboard_url
        return context

@login_required
def commission_list(request):
    user_dashboard_url = reverse('home')

    if hasattr(request.user, 'profile'):
        if request.user.role == 'commissioner':
            user_dashboard_url = reverse('commissioner-dashboard')
        elif request.user.role == 'student':
            user_dashboard_url = reverse('student-dashboard')

    commissions = Commission.objects.all()

    print(f"user_dashboard_url resolved: {user_dashboard_url}")

    return render(request, 'app/commission_list.html', {
        'commissions': commissions,
        'user_dashboard_url': user_dashboard_url,
    })

@login_required
def commissioner_inbox(request):
    profile = get_object_or_404(Profile, user=request.user)

    if not profile.user.is_commissioner():
        return HttpResponseForbidden("You are not authorized to view this page.")

    messages = Message.objects.filter(recipient=request.user).select_related('sender')
    unique_conversations = {}
    for message in messages.order_by('sender', '-timestamp'):
        if message.sender not in unique_conversations:
            unique_conversations[message.sender] = message  # Grab the latest message per sender

    senders_data = [
        {
            'profile': sender.profile,
            'last_message': last_message,
            'unread_count': Message.objects.filter(
                sender=sender, recipient=request.user, is_read=False
            ).count(),
        }
        for sender, last_message in unique_conversations.items()
    ]

    context = {
        'senders': senders_data,
    }

    return render(request, 'app/commissioner/inbox.html', context)


@login_required
def student_inbox(request):
    profile = get_object_or_404(Profile, user=request.user)

    if not profile.user.is_student():
        return HttpResponseForbidden("You are not authorized to access this page.")

    messages = Message.objects.filter(sender=request.user).select_related('recipient', 'recipient__profile')

    unique_conversations = {}
    for message in messages.order_by('recipient', '-timestamp'):
        if message.recipient not in unique_conversations:
            unique_conversations[message.recipient] = message

    recipients = [
        {
            'profile': recipient.profile,
            'last_message': last_message.content,
            'last_message_time': last_message.timestamp,
            'unread_count': Message.objects.filter(
                sender=request.user, recipient=recipient, is_read=False
            ).count(),
        }
        for recipient, last_message in unique_conversations.items()
    ]

    context = {
        'recipients': recipients,
    }

    return render(request, 'app/student/inbox.html', context)


@login_required
def student_conversation_view(request, recipient_pk):
    profile = get_object_or_404(Profile, user=request.user)

    if not profile.user.is_student():
        return HttpResponseForbidden("You are not authorized to access this page.")

    recipient = get_object_or_404(Profile, user__pk=recipient_pk)

    chat_messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(recipient=recipient.user)) |
        (models.Q(sender=recipient.user) & models.Q(recipient=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')

        if not content or not content.strip():
            messages.error(request, "Reply content cannot be empty.")
            return redirect('student-conversation', recipient_pk=recipient_pk)

        Message.objects.create(
            sender=request.user,
            recipient=recipient.user,
            content=content.strip()
        )

        messages.success(request, f"Your message to {recipient.user.username} was sent!")
        return redirect('student-conversation', recipient_pk=recipient_pk)

    context = {
        'recipient': recipient,
        'chat_messages': chat_messages,
    }

    return render(request, 'app/student/conversation.html', context)

@login_required
def conversation_view(request, sender_pk):
    profile = get_object_or_404(Profile, user=request.user)

    if not profile.user.is_commissioner():
        return HttpResponseForbidden("You are not authorized to access this page.")

    sender = get_object_or_404(Profile, user__pk=sender_pk)

    chat_messages = Message.objects.filter(
        models.Q(sender=request.user, recipient=sender.user) |
        models.Q(sender=sender.user, recipient=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')

        if not content or not content.strip():
            messages.error(request, "Reply content cannot be empty.")
            return redirect('conversation', sender_pk=sender_pk)

        Message.objects.create(
            sender=request.user,
            recipient=sender.user,
            content=content.strip()
        )

        messages.success(request, f"Your reply to {sender.user.username} was sent!")
        return redirect('conversation', sender_pk=sender_pk)

    context = {
        'sender': sender,
        'chat_messages': chat_messages,
    }

    return render(request, 'app/commissioner/conversation.html', context)

@login_required
def reply_message(request, recipient_pk):
    from django.shortcuts import get_object_or_404

    recipient = get_object_or_404(Profile, user__pk=recipient_pk)

    if not request.user.profile.is_commissioner():
        return HttpResponseForbidden("You are not authorized to reply to this user.")

    if request.method == 'POST':
        content = request.POST.get('content')

        if not content or not content.strip():
            messages.error(request, "Reply content cannot be empty.")
            return redirect('commissioner-inbox')

        Message.objects.create(
            sender=request.user,
            recipient=recipient.user,
            content=content
        )

        messages.success(request, f"Reply sent to {recipient.user.username}!")
        return redirect('commissioner-inbox')

class CommissionCreateView(LoginRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('commission-list')

    def form_valid(self, form):
        form.instance.commissioner = self.request.user
        return super().form_valid(form)

class CommissionDetailView(LoginRequiredMixin, DetailView):
    model = Commission
    template_name = 'app/commission_detail.html'
    context_object_name = 'commission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.object

        root_comments = Comment.objects.filter(
            commission=commission,
            parent__isnull=True
        ).prefetch_related(
            Prefetch('replies', queryset=Comment.objects.order_by('created_at'))  # Prefetch nested replies
        ).order_by('-created_at')

        context['comments'] = root_comments

        user = self.request.user
        if hasattr(user, 'profile') and user.profile.user.is_student() and commission.available:
            context['show_avail_button'] = True
        else:
            context['show_avail_button'] = False

        return context

@login_required
def add_comment(request, pk):
    commission = get_object_or_404(Commission, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        if not content:
            messages.error(request, 'Comment cannot be empty.')
            return redirect(commission.get_absolute_url())

        if parent_id:
            parent_comment = get_object_or_404(Comment, pk=parent_id)  # Validate parent exists
            Comment.objects.create(
                commission=commission,
                commenter=request.user,
                content=content,
                parent=parent_comment
            )
            messages.success(request, 'Your reply has been added.')
        else:
            Comment.objects.create(
                commission=commission,
                commenter=request.user,
                content=content
            )
            messages.success(request, 'Your comment has been added.')

        return redirect(commission.get_absolute_url())

@login_required
def update_comment(request, pk):
        comment = get_object_or_404(Comment, pk=pk)

        if comment.commenter != request.user:
            messages.error(request, "You are not allowed to edit this comment.")
            return redirect(comment.commission.get_absolute_url())

        if request.method == 'POST':
            content = request.POST.get('content')
            if content:
                comment.content = content
                comment.save()
                messages.success(request, "Your comment has been updated.")
            else:
                messages.error(request, "Comment content cannot be empty.")

            return redirect(comment.commission.get_absolute_url())

        return render(request, 'app/comment/update_comment.html', {'comment': comment})


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if comment.commenter != request.user:
        messages.error(request, "You are not allowed to delete this comment.")
        return redirect(comment.commission.get_absolute_url())

    if request.method == 'POST':
        comment.delete()  # Delete the comment from the database
        messages.success(request, "Your comment has been deleted.")
        return redirect(comment.commission.get_absolute_url())

    return render(request, 'app/comment/confirm_delete_comment.html', {'comment': comment})


@login_required
def avail_commission(request, pk):
    try:
        commission = Commission.objects.get(pk=pk)

        if not request.user.is_student():
            messages.error(request, "Only students can avail commissions.")
            return redirect(commission.get_absolute_url())

        if not commission.available:
            messages.error(request, "This commission is currently not available.")
            return redirect(commission.get_absolute_url())

        Message.objects.create(
            sender=request.user,
            recipient=commission.commissioner,
            content=f"{request.user.username} has availed your commission titled '{commission.title}'."
        )

        Notification.objects.create(
            recipient=commission.commissioner,
            message=f"{request.user.username} has availed your commission titled '{commission.title}'."
        )

        messages.success(request, f"You have successfully availed the commission '{commission.title}'!")
        return redirect(commission.get_absolute_url())

    except Commission.DoesNotExist:
        messages.error(request, "The requested commission does not exist.")
        return redirect('commission-list')


class CommissionUpdateView(LoginRequiredMixin, UpdateView):
    model = Commission
    fields = ['title', 'description', 'price', 'available']
    template_name = 'app/commission_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Commission.objects.filter(commissioner=self.request.user)

class CommissionDeleteView(LoginRequiredMixin, DeleteView):
    model = Commission
    template_name = 'app/commission_confirm_delete.html'
    success_url = reverse_lazy('commission-list')

    def get_queryset(self):
        return Commission.objects.filter(commissioner=self.request.user)

def logout_view(request):
    logout(request)
    return redirect('login')

@require_POST
@login_required
def send_message_view(request, recipient_pk):
    from django.shortcuts import get_object_or_404

    recipient = get_object_or_404(Profile, user__pk=recipient_pk)

    if not recipient.user.is_commissioner():
        return HttpResponseForbidden("You can only message commissioners.")

    if request.method == 'POST':
        content = request.POST.get('content')

        if not content or not content.strip():
            messages.error(request, "Message content cannot be empty.")
            return HttpResponseRedirect(reverse('commissioner-profile', args=[recipient_pk]))

        Message.objects.create(
            sender=request.user,
            recipient=recipient.user,
            content=content
        )
        messages.success(request, "Your message was sent successfully!")
        return HttpResponseRedirect(reverse('commissioner-profile', args=[recipient_pk]))

    return HttpResponseRedirect(reverse('commissioner-profile', args=[recipient_pk]))

class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    context_object_name = 'notifications'
    template_name = 'app/notifications.html'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

@method_decorator(login_required, name='dispatch')
class CommissionDashboardView(TemplateView):
    template_name = "app/commissioner/commissioner_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Commission Dashboard"
        return context

@method_decorator(login_required, name='dispatch')
class StudentDashboardView(TemplateView):
    template_name = "app/student/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Student Dashboard"
        return context


@login_required
def save_commission(request, commission_id):
    commission = get_object_or_404(Commission, id=commission_id)
    student, created = Student.objects.get_or_create(user=request.user)
    student.saved_commissions.add(commission)
    return redirect('saved-commissions')

@login_required
def unsave_commission(request, commission_id):
    commission = get_object_or_404(Commission, id=commission_id)
    student = request.user.student
    student.saved_commissions.remove(commission)
    return redirect('saved-commissions')

@login_required
def saved_commissions(request):
    student = request.user.student
    commissions = student.saved_commissions.all()
    return render(request, 'app/student/saved_commission.html', {'commissions': commissions})

@login_required
def delete_conversation(request, user_pk):
    """
    Deletes all messages between the logged-in user and the given user_pk.
    """
    if request.method == 'POST':
        # Get the logged-in user's profile to check their role
        profile = get_object_or_404(Profile, user=request.user)

        # Ensure the logged-in user is authorized (student or commissioner)
        if not (profile.user.is_student() or profile.user.is_commissioner()):
            return HttpResponseForbidden("You are not authorized to perform this action.")

        # Get the other user involved in the conversation
        other_user = get_object_or_404(Profile, user__pk=user_pk)

        # Delete messages where the logged-in user is either the sender or recipient
        Message.objects.filter(
            Q(sender=request.user, recipient=other_user.user) |
            Q(sender=other_user.user, recipient=request.user)
        ).delete()

        # Add a success message for feedback
        messages.success(request, "Conversation deleted successfully.")

        # Redirect to the correct inbox based on the user role
        if profile.user.is_student():
            return redirect('student-inbox')
        elif profile.user.is_commissioner():
            return redirect('commissioner-inbox')

    # Forbid non-POST requests
    return HttpResponseForbidden("Invalid request method.")

