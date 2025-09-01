from django.contrib import admin
from .models import (
    Broker, Car, ClientRequest, Agreement,
    ProcessedSale, SoldCar, TransactionHistory,SidebarSection,SidebarItem,ViewingRequest
)

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'name', 'email', 'phone')
    search_fields = ('name', 'email')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'make', 'model', 'year', 'price', 'is_sold')
    list_filter = ('make', 'year', 'is_sold')
    search_fields = ('make', 'model', 'reference_number')

@admin.register(ClientRequest)
class ClientRequestAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'client_name', 'car', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client_name', 'client_email', 'reference_number')

@admin.register(ViewingRequest)
class ViewingRequestAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'client_name', 'car', 'status', 'preferred_datetime', 'broker')
    list_filter = ('status', 'preferred_datetime', 'broker')
    search_fields = ('client_name', 'client_email', 'reference_number', 'car__make', 'car__model')

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'client_name', 'sold_car_id', 'car_model', 'sold_date']
    search_fields = ('reference_number',)

@admin.register(ProcessedSale)
class ProcessedSaleAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'viewing_request', 'viewer_name', 'final_price', 'sale_date')
    search_fields = ('viewer_name', 'reference_number')

@admin.register(SoldCar)
class SoldCarAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'car', 'sold_at')
    search_fields = ('reference_number', 'car__reference_number')

@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'sold_car', 'transaction_date', 'amount', 'payment_method')
    search_fields = ('reference_number', 'payment_method')

@admin.register(SidebarSection)
class SidebarSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order',)

@admin.register(SidebarItem)
class SidebarItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'url', 'icon', 'order')
    list_filter = ('section',)
    ordering = ('section', 'order')
    search_fields = ('title', 'url', 'icon')
    # Optional: Add help text or widget for icon field