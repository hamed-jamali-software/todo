from django.db import models
from django.utils import timezone
from datetime import timedelta

# Choices for task status
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
]

# Choices for task duration
DURATION_CHOICES = [
    (15, '15 minutes'),
    (30, '30 minutes'),
    (60, '1 hour'),
    (120, '2 hours'),
]

# Choices for task repetition
REPEAT_CHOICES = [
    ('none', 'None'),
    ('daily', 'Daily'),
    ('every_other_day', 'Every Other Day'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')  # Hex color code
    default_duration = models.IntegerField(choices=DURATION_CHOICES, default=60)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(choices=DURATION_CHOICES, default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    repeat = models.CharField(max_length=20, choices=REPEAT_CHOICES, default='none')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.CharField(max_length=7, default='#000000')  # Hex color code
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timedelta(minutes=self.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
