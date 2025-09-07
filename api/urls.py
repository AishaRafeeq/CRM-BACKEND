from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    BrokerViewSet, CarViewSet, ClientRequestViewSet, AgreementViewSet,
    ProcessedSaleViewSet, SoldCarViewSet, TransactionHistoryViewSet,
    SidebarSectionViewSet, ViewingRequestViewSet, SalesAnalyticsView,FollowUpViewSet,OnDemandCarViewSet,OnDemandViewViewSet,OnDemandLeadViewSet,OnDemandSaleViewSet,OnDemandHistoryViewSet
)

router = DefaultRouter()
router.register(r'brokers', BrokerViewSet)
router.register(r'cars', CarViewSet)
router.register(r'clientrequests', ClientRequestViewSet)
router.register(r'agreements', AgreementViewSet)
router.register(r'processedsales', ProcessedSaleViewSet)
router.register(r'soldcars', SoldCarViewSet)
router.register(r'transactionhistory', TransactionHistoryViewSet)
router.register(r'sidebarsections', SidebarSectionViewSet)
router.register(r'viewings', ViewingRequestViewSet)
router.register(r'followups', FollowUpViewSet)

router.register(r'on-demand-cars', OnDemandCarViewSet, basename='on-demand-cars')
router.register(r'on-demand-views', OnDemandViewViewSet, basename='on-demand-views')
router.register(r'on-demand-leads', OnDemandLeadViewSet, basename='on-demand-leads')
router.register(r'on-demand-sales', OnDemandSaleViewSet, basename='on-demand-sales')
router.register(r'on-demand-history', OnDemandHistoryViewSet, basename='on-demand-history')


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('analytics/', SalesAnalyticsView.as_view(), name='sales-analytics'),
    path('', include(router.urls)),
]
