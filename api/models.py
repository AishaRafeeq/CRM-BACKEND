from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.utils.timezone import now
import os
import random
import string



def generate_reference():
    return str(uuid.uuid4()).replace('-', '').upper()[:12]

class Broker(models.Model):
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.reference_number})"



def generate_reference():
    # Generate a unique 12-character reference
    return str(uuid.uuid4()).replace("-", "")[:12]

def car_image_upload_path(instance, filename):
    # Store images in 'cars/<reference_number>/<filename>'
    return os.path.join('cars', instance.reference_number, filename)

class Car(models.Model):
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference, editable=False)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=car_image_upload_path, blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year}) - Ref: {self.reference_number}"

class ClientRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)  # Admin notes
    preferred_datetime = models.DateTimeField(null=True, blank=True)  # <-- Add this line

    def __str__(self):
        return f"Request {self.reference_number} by {self.client_name} - {self.status}"

class ViewingRequest(models.Model):
    reference_number = models.CharField(
        max_length=12,
        unique=True,
        default=generate_reference
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='viewing_requests')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    preferred_datetime = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)  # client notes / request info
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('sold', 'Sold'),  # Added 'sold' status
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Viewing Request {self.reference_number} for {self.client_name} - {self.car.make} {self.car.model}"

class Agreement(models.Model):
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    client_name = models.CharField(max_length=100, default="Unknown")
    sold_car_id = models.CharField(max_length=12, default="", blank=True, null=True)  # <-- allow manual entry
    car_model = models.CharField(max_length=100, null=True, blank=True, default="Unknown")
    car_color = models.CharField(max_length=50, null=True, blank=True, default="Unknown")
    car_year = models.PositiveIntegerField(default=2024)
    sold_date = models.DateTimeField(default=timezone.now)
    agreement_file = models.FileField(upload_to='agreements/', blank=True, null=True, default=None)
    terms = models.TextField(blank=True, null=True, default="")
    signed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Agreement {self.reference_number} for {self.client_name}"

# models.py
from django.db import models
from django.utils import timezone

PAYMENT_METHOD_CHOICES = [
    ('cash', 'Cash'),
    ('card', 'Card'),
    ('bank_transfer', 'Bank Transfer'),
    ('financing', 'Financing'),
]

PAID_STATUS_CHOICES = [
    ('paid', 'Paid'),
    ('pending', 'Pending'),
    ('failed', 'Failed'),
]

class ProcessedSale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank'),  # <-- Add this line if missing
        ('other', 'Other'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    viewing_request = models.OneToOneField(ViewingRequest, on_delete=models.CASCADE, null=True, blank=True)
    viewer_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bargained_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(default=timezone.now)
    customer_details = models.TextField()
    notes = models.TextField(blank=True, null=True)

    # ✅ New fields
    paid_status = models.CharField(max_length=10, choices=PAID_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Processed Sale {self.reference_number} - Final Price: {self.final_price}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.viewing_request:
            self.handle_sale_workflow()

    def handle_sale_workflow(self):
        """Handle the complete sale workflow"""
        if not self.viewing_request:
            return

        car = self.viewing_request.car
        car.is_sold = True
        car.save(update_fields=['is_sold', 'updated_at'])

        # Update all viewing requests for this car to 'sold' status
        ViewingRequest.objects.filter(car=car).update(status='sold')

        # Only create SoldCar if one does not already exist for this car
        if not SoldCar.objects.filter(car=car).exists():
            SoldCar.objects.create(
                car=car,
                processed_sale=self
            )

class SoldCar(models.Model):
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    car = models.OneToOneField(Car, on_delete=models.CASCADE)
    processed_sale = models.OneToOneField(ProcessedSale, on_delete=models.CASCADE)
    sold_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Sold Car {self.reference_number} - {self.car}"

class TransactionHistory(models.Model):
    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    sold_car = models.ForeignKey(SoldCar, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.reference_number} - {self.amount} on {self.transaction_date}"

class SidebarSection(models.Model):
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

class SidebarItem(models.Model):
    section = models.ForeignKey(SidebarSection, related_name='items', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255)  # frontend route or external link
    icon = models.CharField(max_length=50, blank=True, null=True)  # optional icon class or name
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.section.title} - {self.title}"

    class Meta:
        ordering = ['order']

def generate_reference():
    return str(uuid.uuid4().hex[:10]).upper()

class FollowUp(models.Model):
    SOURCE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('qatar_living', 'Qatar Living'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('closed', 'Closed'),
    ]

    reference_number = models.CharField(max_length=12, unique=True, default=generate_reference)
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_address = models.TextField(blank=True, null=True)

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='followups', null=False, default=1)
    car_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bargained_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')
    notes = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_closed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def close(self):
        self.status = 'closed'
        self.is_closed = True
        self.save(update_fields=['status', 'is_closed', 'updated_at'])

    def __str__(self):
        return f"FollowUp {self.reference_number} - {self.client_name} ({self.source})"
    

    

# 1️⃣ Define the upload path function first
def on_demand_car_image_path(instance, filename):
    return f'on_demand_cars/{instance.reference_number}/{filename}'

# 2️⃣ Define the reference number generator
def generate_on_demand_ref(make='CAR'):
    """
    Generate 8-character reference: first 3 letters of make + 5 random digits
    """
    prefix = make[:3].upper() if make else 'CAR'
    digits = ''.join(random.choices(string.digits, k=5))
    return f"{prefix}{digits}"

# 3️⃣ Then define your model
class OnDemandCar(models.Model):
    reference_number = models.CharField(max_length=8, unique=True, editable=False)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=on_demand_car_image_path, blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ Free-text fields
    broker_name = models.CharField(max_length=100, blank=True, null=True)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    owner_contact = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = generate_on_demand_ref(self.make)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"On-Demand: {self.make} {self.model} ({self.reference_number})"
