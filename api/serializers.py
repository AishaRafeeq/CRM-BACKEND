from rest_framework import serializers
from .models import (
    Broker, Car, ClientRequest, Agreement, ProcessedSale, SoldCar, 
    TransactionHistory, SidebarSection, SidebarItem, ViewingRequest,FollowUp,OnDemandCar,OnDemandView,OnDemandLead,OnDemandSale,OnDemandHistory,OnDemandEnquiry
)
from django.utils import timezone
from datetime import datetime


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = '__all__'


class CarSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Car
        fields = '__all__'


class CarDetailSerializer(serializers.ModelSerializer):
    """Detailed car serializer with additional computed fields"""
    total_viewing_requests = serializers.SerializerMethodField()
    sold_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = '__all__'
    
    def get_total_viewing_requests(self, obj):
        return obj.viewing_requests.count()
    
    def get_sold_status(self, obj):
        if obj.is_sold:
            return "Sold"
        return "Available"


class ClientRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRequest
        fields = '__all__'


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = [
            'id', 'reference_number', 'client_name', 'sold_car_id',
            'car_model', 'car_color', 'car_year', 'sold_date',
            'agreement_file', 'terms', 'signed_at'
        ]
        read_only_fields = ['reference_number', 'signed_at']


class ProcessedSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedSale
        fields = [
            'id', 'reference_number', 'viewing_request', 'viewer_name',
            'price', 'bargained_price', 'final_price', 'sale_date',
            'customer_details', 'notes', 'payment_method', 'paid_status'
        ]
        extra_kwargs = {
            'viewing_request': {'required': True}
        }


class SoldCarSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    processed_sale = ProcessedSaleSerializer(read_only=True)

    class Meta:
        model = SoldCar
        fields = '__all__'


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'


class SidebarSectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = SidebarSection
        fields = ['id', 'title', 'order', 'items']
    
    def get_items(self, obj):
        items = obj.items.all()
        return [
            {
                'id': item.id,
                'title': item.title,
                'url': item.url,
                'icon': item.icon,
                'order': item.order
            }
            for item in items
        ]


class ViewingRequestSerializer(serializers.ModelSerializer):
    car_details = serializers.SerializerMethodField()
    broker_details = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    class Meta:
        model = ViewingRequest
        fields = '__all__'

    def get_car_details(self, obj):
        request = self.context.get('request')
        image_url = None
        if obj.car and obj.car.image:
            if request:
                image_url = request.build_absolute_uri(obj.car.image.url)
            else:
                image_url = obj.car.image.url
        return {
            'id': obj.car.id,
            'reference_number': obj.car.reference_number,
            'make': obj.car.make,
            'model': obj.car.model,
            'year': obj.car.year,
            'price': obj.car.price,
            'description': obj.car.description,
            'image': image_url,
            'is_sold': obj.car.is_sold,
            'created_at': obj.car.created_at,
        }

    def get_broker_details(self, obj):
        broker = obj.broker
        if not broker:
            return None
        return {
            'id': broker.id,
            'name': broker.name,
            'email': broker.email,
            'phone': broker.phone,
        }

    def get_status_info(self, obj):
        status_colors = {
            'pending': 'yellow',
            'interested': 'green',
            'not_interested': 'red',
            'sold': 'gray',
        }
        return {
            'status': obj.status,
            'color': status_colors.get(obj.status, 'blue'),
            'label': dict(ViewingRequest.STATUS_CHOICES).get(obj.status, obj.status),
        }



class ViewingRequestSummarySerializer(serializers.ModelSerializer):
    car_make_model = serializers.SerializerMethodField()
    car_price = serializers.SerializerMethodField()
    car_image = serializers.SerializerMethodField()
    broker_name = serializers.SerializerMethodField()
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ViewingRequest
        fields = [
            'id', 'reference_number', 'car_make_model', 'car_price', 'car_image',
            'client_name', 'client_email', 'client_phone', 'preferred_datetime',
            'broker_name', 'created_at', 'days_ago', 'status'
        ]
    
    def get_car_make_model(self, obj):
        if obj.car.is_sold:
            return f"{obj.car.make} {obj.car.model} (SOLD)"
        return f"{obj.car.make} {obj.car.model}"
    
    def get_car_price(self, obj):
        if obj.car.is_sold:
            return "SOLD"
        return f"${obj.car.price:,.2f}"
    
    def get_car_image(self, obj):
        if obj.car.image:
            return obj.car.image.url
        return None
    
    def get_broker_name(self, obj):
        return obj.broker.name if obj.broker else None
    
    def get_days_ago(self, obj):
        delta = timezone.now() - obj.created_at
        return delta.days


class ViewingRequestDetailSerializer(serializers.ModelSerializer):
    car_details = serializers.SerializerMethodField()
    broker_details = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    class Meta:
        model = ViewingRequest
        fields = [
            'id',
            'reference_number',
            'client_name',
            'client_email',
            'client_phone',
            'preferred_datetime',
            'status',
            'created_at',
            'updated_at',
            'notes',
            'car_details',
            'broker_details',
            'status_info',
        ]

    def get_car_details(self, obj):
        car = obj.car
        if not car:
            return None
        request = self.context.get('request')
        image_url = None
        if car.image:
            if request:
                image_url = request.build_absolute_uri(car.image.url)
            else:
                image_url = car.image.url
        return {
            'id': car.id,
            'reference_number': car.reference_number,
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'price': car.price,
            'description': car.description,
            'image': image_url,
            'is_sold': car.is_sold,
            'created_at': car.created_at,
        }

    def get_broker_details(self, obj):
        broker = obj.broker
        if not broker:
            return None
        return {
            'id': broker.id,
            'reference_number': getattr(broker, 'reference_number', None),
            'name': broker.name,
            'email': broker.email,
            'phone': broker.phone,
        }

    def get_status_info(self, obj):
        status_colors = {
            'pending': 'yellow',
            'interested': 'green',
            'not_interested': 'red',
            'sold': 'gray',
        }
        return {
            'status': obj.status,
            'color': status_colors.get(obj.status, 'blue'),
            'label': dict(ViewingRequest.STATUS_CHOICES).get(obj.status, obj.status),
        }



# Analytics Serializers
class AnalyticsSeriesPointSerializer(serializers.Serializer):
    period_start = serializers.DateTimeField()
    amount = serializers.FloatField()
    cars = serializers.IntegerField()


class SalesAnalyticsTotalsSerializer(serializers.Serializer):
    total_cars_sold = serializers.IntegerField()
    total_sales_amount = serializers.FloatField()
    upcoming_views = serializers.IntegerField()
    pending_viewings = serializers.IntegerField()
    interested_viewings = serializers.IntegerField()
    not_interested_viewings = serializers.IntegerField()


class SalesAnalyticsSeriesSerializer(serializers.Serializer):
    weekly = AnalyticsSeriesPointSerializer(many=True)
    monthly = AnalyticsSeriesPointSerializer(many=True)
    yearly = AnalyticsSeriesPointSerializer(many=True)


class SalesAnalyticsSerializer(serializers.Serializer):
    totals = SalesAnalyticsTotalsSerializer()
    series = SalesAnalyticsSeriesSerializer()


class SoldCarDetailSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)
    processed_sale = ProcessedSaleSerializer(read_only=True)

    class Meta:
        model = SoldCar
        fields = '__all__'


class FollowUpSerializer(serializers.ModelSerializer):
    car_details = serializers.SerializerMethodField()

    class Meta:
        model = FollowUp
        fields = [
            'id', 'reference_number', 'client_name', 'client_phone',
            'car', 'car_details', 'notes', 'source', 'status', 'is_closed', 'created_at', 'updated_at'
        ]

    def get_car_details(self, obj):
        car = obj.car
        if not car:
            return None
        return {
            'id': car.id,
            'reference_number': car.reference_number,
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'is_sold': car.is_sold,
        }
class OnDemandCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnDemandCar
        fields = [
            'id', 'reference_number', 'make', 'model', 'year', 'price',
            'company_commission', 'broker_name', 'broker_contact', 'description', 'image',
            'is_sold', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reference_number', 'created_at', 'updated_at']


class OnDemandEnquirySerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=OnDemandCar.objects.all())

    class Meta:
        model = OnDemandEnquiry
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']


class OnDemandViewSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=OnDemandCar.objects.all())

    class Meta:
        model = OnDemandView
        fields = "__all__"


class OnDemandLeadSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=OnDemandCar.objects.all())

    view = OnDemandViewSerializer(read_only=True)
    view_id = serializers.PrimaryKeyRelatedField(queryset=OnDemandView.objects.filter(status='interested'), source='view', write_only=True)

    class Meta:
        model = OnDemandLead
        fields = ["id", "view", "view_id", "status", "created_at"]


class OnDemandSaleSerializer(serializers.ModelSerializer):
    lead = OnDemandLeadSerializer(read_only=True)
    lead_id = serializers.PrimaryKeyRelatedField(queryset=OnDemandLead.objects.filter(status='positive'), source='lead', write_only=True)

    class Meta:
        model = OnDemandSale
        fields = ["id", "lead", "lead_id", "final_price", "company_commission", "sold_at"]


class OnDemandHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OnDemandHistory
        fields = "__all__"