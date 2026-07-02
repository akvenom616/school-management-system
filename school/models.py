import os
import secrets
import string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def generate_random_password(length=12):
    """Generate a strong random password that satisfies the app policy."""
    length = max(10, min(length, 12))
    characters = string.ascii_letters + string.digits + string.punctuation

    while True:
        password = ''.join(secrets.choice(characters) for _ in range(length))
        if (
            any(char.isupper() for char in password)
            and any(char.islower() for char in password)
            and any(char.isdigit() for char in password)
            and any(not char.isalnum() for char in password)
        ):
            return password


def validate_homework_file(value):
    allowed_extensions = {'.pdf', '.doc', '.docx'}
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Only PDF, DOC, and DOCX files are allowed for homework uploads.')


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    class_name = models.CharField(max_length=50)
    dob = models.DateField(null=True, blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    
    # Authentication
    student_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"


class FeeComponent(models.Model):
    """Global fee components that admin creates."""
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]
    
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - Rs. {self.amount}/{self.frequency}"


class StudentFeeComponent(models.Model):
    """Student-specific fee components."""
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_components')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['student', 'name']
    
    def __str__(self):
        return f"{self.student.name} - {self.name}"


class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.name} - Rs. {self.amount} ({self.date})"


class StudentMessage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='messages')
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Message to {self.student.name}: {self.title}"


class Homework(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    class_name = models.CharField(max_length=100)
    due_date = models.DateField(null=True, blank=True)
    file = models.FileField(
        upload_to='homework_files/',
        validators=[validate_homework_file],
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.class_name})"


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return self.title
