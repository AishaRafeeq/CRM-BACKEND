from .models import (
    Broker, Car, ClientRequest, Agreement,
    ProcessedSale, SoldCar, TransactionHistory,SidebarSection,SidebarItem,ViewingRequest,FollowUp,OnDemandCar,OnDemandView,OnDemandLead,OnDemandSale,OnDemandHistory
)
from .serializers import (
    BrokerSerializer, CarSerializer, ClientRequestSerializer,
    AgreementSerializer, ProcessedSaleSerializer,
    SoldCarSerializer, TransactionHistorySerializer, SidebarSectionSerializer,
    ViewingRequestSerializer, ViewingRequestDetailSerializer, ViewingRequestSummarySerializer,FollowUpSerializer,OnDemandCarSerializer,OnDemandViewSerializer,OnDemandLeadSerializer,OnDemandSaleSerializer,OnDemandHistorySerializer
)
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny



from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from .serializers import SalesAnalyticsSerializer


class BrokerViewSet(viewsets.ModelViewSet):
    queryset = Broker.objects.all()
    serializer_class = BrokerSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reference_number', 'name', 'email', 'phone']
    filterset_fields = ['reference_number', 'name', 'email', 'phone']
    ordering_fields = ['name', 'reference_number', 'id']
    ordering = ['name']

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        # Only return cars that are not sold
        return Car.objects.filter(is_sold=False)
    
    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        available_cars = Car.objects.filter(is_sold=False)
        serializer = self.get_serializer(available_cars, many=True)
        return Response(serializer.data)

class ClientRequestViewSet(viewsets.ModelViewSet):
    queryset = ClientRequest.objects.all()
    serializer_class = ClientRequestSerializer
    permission_classes = [AllowAny]

    search_fields = ['reference_number', 'client_name', 'client_email', 'client_phone']
    filterset_fields = ['status', 'car', 'created_at']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        """Mark client request as accepted and move to viewing requests"""
        client_request = self.get_object()
        client_request.status = "accepted"
        client_request.save(update_fields=["status"])

        # Use the correct field for scheduled date/time
        viewing_request = ViewingRequest.objects.create(
            reference_number=f"VW-{client_request.reference_number}",
            client_name=client_request.client_name,
            client_email=client_request.client_email,
            client_phone=client_request.client_phone,
            car=client_request.car,
            preferred_datetime=client_request.preferred_datetime,  # <-- FIX: use the correct field name
            status="pending",
            notes=f"Created automatically from ClientRequest {client_request.id}"
        )

        return Response({
            "status": "accepted",
            "viewing_request_id": viewing_request.id,
            "message": f"Client request {client_request.reference_number} moved to ViewingRequest"
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Mark client request as rejected"""
        client_request = self.get_object()
        client_request.status = "rejected"
        client_request.save(update_fields=["status"])  # ✅ FIXED
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)

class AgreementViewSet(viewsets.ModelViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reference_number', 'client_name', 'car_model']
    filterset_fields = ['sold_date', 'client_name']  # <--- NO 'scheduled_view'
    ordering_fields = ['sold_date', 'signed_at']
    ordering = ['-sold_date']

class ProcessedSaleViewSet(viewsets.ModelViewSet):
    queryset = ProcessedSale.objects.all()
    serializer_class = ProcessedSaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    search_fields = ['reference_number', 'viewer_name']
    filterset_fields = [
        'payment_method', 'paid_status', 'sale_date', 'final_price'
    ]
    ordering_fields = ['sale_date', 'final_price']
    ordering = ['-sale_date']
    lookup_field = 'reference_number'  # Allow detail fetch by reference_number

    def perform_create(self, serializer):
        sale = serializer.save()
        # Sale workflow is handled in the model's save()

    def get_queryset(self):
        queryset = super().get_queryset()
        # Optional: add custom filtering logic if needed
        return queryset

class SoldCarViewSet(viewsets.ModelViewSet):
    queryset = SoldCar.objects.all()
    serializer_class = SoldCarSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reference_number', 'car__make', 'car__model']
    filterset_fields = ['sold_at', 'car']
    ordering_fields = ['sold_at']
    ordering = ['-sold_at']

class TransactionHistoryViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reference_number', 'payment_method']
    filterset_fields = ['transaction_date', 'amount', 'sold_car'
    ]
    ordering_fields = ['transaction_date', 'amount']
    ordering = ['-transaction_date']

class SidebarSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SidebarSection.objects.prefetch_related('items').all()
    serializer_class = SidebarSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

class ViewingRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for booking and managing car viewings.
    """
    queryset = ViewingRequest.objects.select_related('car', 'broker').all().order_by('-created_at')
    serializer_class = ViewingRequestSerializer
    permission_classes = [AllowAny]

    pagination_class = PageNumberPagination
    search_fields = ['reference_number', 'client_name', 'client_email', 'client_phone', 'car__make', 'car__model', 'broker__name']
    filterset_fields = ['status', 'broker', 'car', 'preferred_datetime', 'created_at']
    ordering_fields = ['created_at', 'preferred_datetime']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ViewingRequestSummarySerializer
        elif self.action == 'retrieve':
            return ViewingRequestDetailSerializer
        return ViewingRequestSerializer

    def perform_create(self, serializer):
        if not serializer.validated_data.get('broker'):
            default_broker = Broker.objects.first()
            serializer.save(broker=default_broker)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def mark_interested(self, request, pk=None):
        viewing = self.get_object()
        viewing.status = 'interested'
        viewing.save(update_fields=['status', 'updated_at'])
        return Response({'status': viewing.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_not_interested(self, request, pk=None):
        viewing = self.get_object()
        viewing.status = 'not_interested'
        viewing.save(update_fields=['status', 'updated_at'])
        return Response({'status': viewing.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_sold(self, request, pk=None):
        """Mark viewing request as sold and handle sale workflow"""
        viewing = self.get_object()
        viewing.status = 'sold'
        viewing.save(update_fields=['status', 'updated_at'])
        
        # Mark car as sold
        car = viewing.car
        car.is_sold = True
        car.save(update_fields=['is_sold', 'updated_at'])
        
        # Update all viewing requests for this car to 'sold' status
        ViewingRequest.objects.filter(car=car).update(status='sold')
        
        return Response({
            'status': viewing.status,
            'car_id': car.id,
            'message': f'Car {car.make} {car.model} marked as sold'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def schedule_view(self, request, pk=None):
        """Schedule a viewing for a specific date/time"""
        viewing = self.get_object()
        scheduled_datetime = request.data.get('scheduled_datetime')
        broker_id = request.data.get('broker_id')
        notes = request.data.get('notes', '')
        
        if not scheduled_datetime:
            return Response({'error': 'scheduled_datetime is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update viewing request with scheduled datetime
        viewing.preferred_datetime = scheduled_datetime
        viewing.notes = notes
        if broker_id:
            viewing.broker_id = broker_id
        viewing.save()
        
        return Response({
            'id': viewing.id,
            'scheduled_datetime': viewing.preferred_datetime,
            'broker': viewing.broker.name if viewing.broker else None,
            'message': f'Viewing scheduled for {viewing.preferred_datetime}'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reschedule_view(self, request, pk=None):
        """Reschedule an existing viewing"""
        viewing = self.get_object()
        new_datetime = request.data.get('scheduled_datetime')
        notes = request.data.get('notes', viewing.notes)
        
        if not new_datetime:
            return Response({'error': 'scheduled_datetime is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        viewing.preferred_datetime = new_datetime
        viewing.notes = notes
        viewing.save()
        
        return Response({
            'id': viewing.id,
            'scheduled_datetime': viewing.preferred_datetime,
            'message': f'Viewing rescheduled for {viewing.preferred_datetime}'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel_view(self, request, pk=None):
        """Cancel a scheduled viewing"""
        viewing = self.get_object()
        viewing.preferred_datetime = None
        viewing.save()
        
        return Response({
            'id': viewing.id,
            'message': 'Viewing cancelled successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_status(self, request):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({'error': 'ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        updated = ViewingRequest.objects.filter(id__in=ids).update(status='pending')
        return Response({'updated': updated}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_viewings = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        page = self.paginate_queryset(recent_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(recent_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        upcoming_viewings = self.get_queryset().filter(
            preferred_datetime__gte=timezone.now()
        ).order_by('preferred_datetime')
        page = self.paginate_queryset(upcoming_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(upcoming_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_viewings = self.get_queryset().filter(
            preferred_datetime__lt=timezone.now()
        ).order_by('-preferred_datetime')
        page = self.paginate_queryset(overdue_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(overdue_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Get all scheduled viewings (with preferred_datetime set)"""
        scheduled_viewings = self.get_queryset().filter(
            preferred_datetime__isnull=False
        ).order_by('preferred_datetime')
        page = self.paginate_queryset(scheduled_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(scheduled_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sold(self, request):
        """Get viewing requests for sold cars"""
        sold_viewings = self.get_queryset().filter(status='sold')
        page = self.paginate_queryset(sold_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(sold_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_car(self, request):
        car_id = request.query_params.get('car_id')
        if not car_id:
            return Response(
                {'error': 'car_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        car_viewings = self.get_queryset().filter(car_id=car_id)
        page = self.paginate_queryset(car_viewings)
        if page is not None:
            serializer = ViewingRequestDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestDetailSerializer(car_viewings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_broker(self, request):
        broker_id = request.query_params.get('broker_id')
        if not broker_id:
            return Response(
                {'error': 'broker_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        broker_viewings = self.get_queryset().filter(broker_id=broker_id)
        page = self.paginate_queryset(broker_viewings)
        if page is not None:
            serializer = ViewingRequestSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ViewingRequestSummarySerializer(broker_viewings, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        car_id = self.request.query_params.get('car')
        client_name = self.request.query_params.get('client_name')
        broker_id = self.request.query_params.get('broker')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        status_filter = self.request.query_params.get('status')

        if car_id:
            queryset = queryset.filter(car__id=car_id)
        if client_name:
            queryset = queryset.filter(client_name__icontains=client_name)
        if broker_id:
            queryset = queryset.filter(broker__id=broker_id)

        if start_date:
            try:
                start_datetime = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__gte=start_datetime)
            except ValueError:
                pass
        if end_date:
            try:
                end_datetime = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(created_at__lte=end_datetime)
            except ValueError:
                pass

        # Discrete status filtering (now includes 'sold')
        if status_filter in ['pending', 'interested', 'not_interested', 'sold']:
            queryset = queryset.filter(status=status_filter)
        elif status_filter:
            # Keep support for time-based filters for backward compatibility
            now = timezone.now()
            if status_filter == 'scheduled':
                queryset = queryset.filter(preferred_datetime__gte=now)
            elif status_filter == 'overdue':
                queryset = queryset.filter(preferred_datetime__lt=now)
            elif status_filter == 'unscheduled':
                queryset = queryset.filter(preferred_datetime__isnull=True)

        return queryset


class SalesAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Totals
        total_cars_sold = SoldCar.objects.count()
        total_sales_amount = ProcessedSale.objects.aggregate(total=Sum('final_price'))['total'] or 0
        upcoming_views = ViewingRequest.objects.filter(preferred_datetime__gte=now).count()
        pending_viewings = ViewingRequest.objects.filter(status='pending').count()
        interested_viewings = ViewingRequest.objects.filter(status='interested').count()
        not_interested_viewings = ViewingRequest.objects.filter(status='not_interested').count()

        # Weekly (last 8 weeks)
        last_8_weeks = ProcessedSale.objects.filter(sale_date__gte=now - timezone.timedelta(weeks=8)) \
            .annotate(week=TruncWeek('sale_date')) \
            .values('week') \
            .annotate(amount=Sum('final_price'), cars=Count('id')) \
            .order_by('week')

        # Monthly (last 12 months)
        last_12_months = ProcessedSale.objects.filter(sale_date__gte=now - timezone.timedelta(weeks=52)) \
            .annotate(month=TruncMonth('sale_date')) \
            .values('month') \
            .annotate(amount=Sum('final_price'), cars=Count('id')) \
            .order_by('month')

        # Yearly (all years)
        yearly = ProcessedSale.objects.annotate(year=TruncYear('sale_date')) \
            .values('year') \
            .annotate(amount=Sum('final_price'), cars=Count('id')) \
            .order_by('year')

        payload = {
            'totals': {
                'total_cars_sold': total_cars_sold,
                'total_sales_amount': float(total_sales_amount),
                'upcoming_views': upcoming_views,
                'pending_viewings': pending_viewings,
                'interested_viewings': interested_viewings,
                'not_interested_viewings': not_interested_viewings,
            },
            'series': {
                'weekly': [
                    {
                        'period_start': item['week'],
                        'amount': float(item['amount'] or 0),
                        'cars': item['cars'],
                    } for item in last_8_weeks
                ],
                'monthly': [
                    {
                        'period_start': item['month'],
                        'amount': float(item['amount'] or 0),
                        'cars': item['cars'],
                    } for item in last_12_months
                ],
                'yearly': [
                    {
                        'period_start': item['year'],
                        'amount': float(item['amount'] or 0),
                        'cars': item['cars'],
                    } for item in yearly
                ],
            }
        }

        serializer = SalesAnalyticsSerializer(payload)
        return Response(serializer.data)

class FollowUpViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.select_related('car').all().order_by('-created_at')
    serializer_class = FollowUpSerializer
    permission_classes = [AllowAny]  # <-- Remove authentication requirement

    search_fields = ['reference_number', 'client_name', 'client_phone', 'source']
    filterset_fields = ['status', 'source', 'car', 'is_closed', 'created_at']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
      followup = self.get_object()
      followup.status = 'pending'
      followup.save(update_fields=['status', 'updated_at'])
      return Response({'status': followup.status}, status=status.HTTP_200_OK)



    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        followup = self.get_object()
        followup.status = 'contacted'
        followup.save(update_fields=['status', 'updated_at'])
        return Response({'status': followup.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_interested(self, request, pk=None):
        followup = self.get_object()
        followup.status = 'interested'
        followup.save(update_fields=['status', 'updated_at'])
        return Response({'status': followup.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def schedule_viewing(self, request, pk=None):
        followup = self.get_object()
        if followup.status != 'interested':
            return Response({'error': 'Viewing can only be scheduled if lead is interested'}, status=400)

        viewing = ViewingRequest.objects.create(
            client_name=followup.client_name,
            client_phone=followup.client_phone,
            car=followup.car,
            notes=followup.notes
        )
        followup.status = 'contacted'
        followup.save(update_fields=['status'])
        return Response({'message': 'Viewing scheduled', 'viewing_id': viewing.id}, status=201)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        followup = self.get_object()
        followup.close()
        return Response({'message': 'FollowUp closed and moved to history'}, status=200)
    
class OnDemandCarViewSet(viewsets.ModelViewSet):
    queryset = OnDemandCar.objects.all().order_by('-created_at')
    serializer_class = OnDemandCarSerializer
    permission_classes = [permissions.IsAuthenticated]  # or AllowAny if public

    search_fields = ['reference_number', 'make', 'model']
    filterset_fields = ['is_sold', 'year', 'make']
    ordering_fields = ['created_at', 'price']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available (unsold) On-Demand cars"""
        cars = self.queryset.filter(is_sold=False)
        serializer = self.get_serializer(cars, many=True)
        return Response(serializer.data)
    
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import OnDemandView, OnDemandHistory, OnDemandLead
from .serializers import OnDemandViewSerializer

class OnDemandViewViewSet(viewsets.ModelViewSet):
    queryset = OnDemandView.objects.all().order_by("-created_at")
    serializer_class = OnDemandViewSerializer

    @action(detail=True, methods=['post'])
    def mark_interested(self, request, pk=None):
        """Mark view as interested (green)"""
        view = self.get_object()
        view.status = 'interested'
        view.save(update_fields=['status', 'updated_at'])
        return Response({'status': view.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_not_interested(self, request, pk=None):
        """Move view to history if not interested"""
        view = self.get_object()
        view.status = 'not_interested'
        view.save(update_fields=['status', 'updated_at'])

        # Move to OnDemandHistory
        OnDemandHistory.objects.create(
            view=view,
            moved_at=timezone.now(),
            reason='Not Interested'
        )
        return Response({'status': 'moved to history'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
        """Revert view to pending"""
        view = self.get_object()
        view.status = 'pending'
        view.save(update_fields=['status', 'updated_at'])
        return Response({'status': view.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def convert_to_lead(self, request, pk=None):
        """Convert interested view to a positive lead"""
        view = self.get_object()
        if view.status != 'interested':
            return Response({'error': 'Only interested views can be converted to leads'}, status=400)

        # Create positive lead
        lead = OnDemandLead.objects.create(
            view=view,
            status='positive_lead',
        )

        # Remove from interested pool
        view.status = 'lead_converted'
        view.save(update_fields=['status', 'updated_at'])

        return Response({'status': 'converted to lead', 'lead_id': lead.id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def interested_clients(self, request):
        """Return all views with status='interested' for dropdown"""
        interested_views = self.queryset.filter(status='interested')
        serializer = self.get_serializer(interested_views, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OnDemandLeadViewSet(viewsets.ModelViewSet):
    queryset = OnDemandLead.objects.all().order_by("-created_at")
    serializer_class = OnDemandLeadSerializer

    def perform_create(self, serializer):
        # Automatically update view status → "interested" → "positive lead"
        lead = serializer.save()
        lead.view.status = "interested"
        lead.view.save()


class OnDemandSaleViewSet(viewsets.ModelViewSet):
    queryset = OnDemandSale.objects.all().order_by("-sold_at")
    serializer_class = OnDemandSaleSerializer

    def perform_create(self, serializer):
        sale = serializer.save()
        # Update lead + car when sold
        lead = sale.lead
        lead.status = "sold"
        lead.save()

        car = lead.view.car
        car.is_sold = True
        car.save()


class OnDemandHistoryViewSet(viewsets.ModelViewSet):
    queryset = OnDemandHistory.objects.all().order_by("-moved_at")
    serializer_class = OnDemandHistorySerializer

    def create(self, request, *args, **kwargs):
        """
        Add to history manually or when lead/view marked lost/not interested
        """
        return super().create(request, *args, **kwargs)