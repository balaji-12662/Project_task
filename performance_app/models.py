# performance_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

REVIEW_TYPES = [
    ('self','self'),
    ('manager','manager'),
    ('peer','peer'),
]

REVIEW_STATUS = [
    ('draft','draft'),
    ('submitted','submitted'),
]

CYCLE_STATUS = [
    ('active','active'),
    ('closed','closed'),
]

CRITERIA_CHOICES = [
    ('technical','technical'),
    ('communication','communication'),
    ('leadership','leadership'),
    ('goals','goals'),
]

GOAL_STATUS = [
    ('not_started','not_started'),
    ('in_progress','in_progress'),
    ('completed','completed'),
]

USER_ROLES = [
    ('employee','employee'),
    ('manager','manager'),
    ('hr','hr'),
]

class Employee(models.Model):
    # mirrors employees table in spec
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, db_index=True)
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    hire_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.name} ({self.email})"

class ReviewCycle(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=CYCLE_STATUS, default='active')

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return self.name

class Review(models.Model):
    employee = models.ForeignKey(Employee, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(Employee, related_name='given_reviews', on_delete=models.CASCADE)
    cycle = models.ForeignKey(ReviewCycle, related_name='reviews', on_delete=models.CASCADE)
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPES)
    status = models.CharField(max_length=10, choices=REVIEW_STATUS, default='draft')
    submitted_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'cycle', 'reviewer', 'review_type')
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['cycle']),
            models.Index(fields=['reviewer']),
        ]

    def __str__(self):
        return f"Review {self.id}: {self.employee} by {self.reviewer} ({self.review_type})"

class Score(models.Model):
    review = models.ForeignKey(Review, related_name='scores', on_delete=models.CASCADE)
    criteria = models.CharField(max_length=20, choices=CRITERIA_CHOICES)
    score = models.IntegerField()
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('review', 'criteria')

class Goal(models.Model):
    employee = models.ForeignKey(Employee, related_name='goals', on_delete=models.CASCADE)
    cycle = models.ForeignKey(ReviewCycle, related_name='goals', on_delete=models.CASCADE)
    description = models.TextField()
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='not_started')
    progress = models.IntegerField(default=0)  # 0-100
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class AuditLog(models.Model):
    entity_type = models.CharField(max_length=50)
    entity_id = models.IntegerField()
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True)
    new_value = models.TextField(null=True)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(default=timezone.now)
