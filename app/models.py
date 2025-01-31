from django.contrib.auth.models import AbstractUser , Group, Permission
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


REQUEST_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('completed', 'Completed'),
]

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5 stars

# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('commissioner', 'Commissioner'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def is_student(self):
        return self.role == 'student'

    def is_commissioner(self):
        return self.role == 'commissioner'


@receiver(post_save, sender=CustomUser )
def create_or_update_user_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    expertise = models.CharField(max_length=255, blank=True, null=True)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='profile_pictures/default.jpg')


    def __str__(self):
        return f"{self.user.username} - Profile"

# Commission QuerySet
class CommissionQuerySet(models.QuerySet):
    def available(self):
        return self.filter(available=True)

    def by_commissioner(self, commissioner):
        return self.filter(commissioner=commissioner)

# Commission Model
class Commission(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    commissioner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commissions_created')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    objects = CommissionQuerySet.as_manager()  # Use the custom QuerySet

    def __str__(self):
        return f"{self.title} - ${self.price}"

    def get_absolute_url(self):
        return reverse('commission-detail', args=[self.pk])

# Student Model
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    saved_commissions = models.ManyToManyField(Commission, blank=True, related_name="saved_by_students")

    def __str__(self):
        return self.user.username

# Comment Model
class Comment(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.commission.title[:15]}..."

# Request QuerySet
class RequestQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status='pending')

    def by_student(self, student):
        return self.filter(student=student)

# Request Model
class Request(models.Model):
    student = models.ForeignKey(CustomUser , on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')

    objects = RequestQuerySet.as_manager()  # Use the custom QuerySet

    def __str__(self):
        return f"Request by {self.student.username} for {self.commission.title}"

# Review Model
class Review(models.Model):
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser , on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.commission.title}"

# Conversation Model
class Conversation(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_conversations')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_conversations')
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.sender} and {self.recipient}"

# Message Model
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.content}"

# Notification Model
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {self.message[:50]}"