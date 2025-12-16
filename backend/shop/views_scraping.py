"""
API views for scraping data
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.core.management import call_command
from django.utils import timezone
import threading

from .models_scraping import CompetitorSite, ScrapedProduct, PriceHistory
from .serializers_scraping import CompetitorSiteSerializer, ScrapedProductSerializer, PriceHistorySerializer


class CompetitorSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for competitor sites
    """
    queryset = CompetitorSite.objects.all()
    serializer_class = CompetitorSiteSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(detail=False, methods=['post'])
    def trigger_scraping(self, request):
        """
        Trigger scraping for all active sites or specific site
        POST /api/competitor-sites/trigger_scraping/
        POST /api/competitor-sites/trigger_scraping/ {"site_id": 1}
        """
        site_id = request.data.get('site_id')

        def run_scraping():
            """Run scraping in background thread"""
            try:
                if site_id:
                    site = CompetitorSite.objects.get(id=site_id)
                    call_command('scrape_competitors', '--site', site.name.lower(), '--force')
                else:
                    call_command('scrape_competitors', '--force')
            except Exception as e:
                print(f"Scraping error: {e}")

        # Run scraping in background thread to avoid blocking the request
        thread = threading.Thread(target=run_scraping)
        thread.start()

        return Response({
            'status': 'started',
            'message': 'Scraping započet u pozadini. Osvežite stranicu za 10-30 sekundi da vidite rezultate.'
        }, status=status.HTTP_202_ACCEPTED)


class ScrapedProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for scraped products

    Filters:
    - site: Filter by competitor site ID
    - category: Filter by category name
    - on_sale: Filter by sale status (true/false)
    - in_stock: Filter by stock status (true/false)

    Search:
    - name, description

    Ordering:
    - current_price, last_seen_at, discount_percentage
    """
    queryset = ScrapedProduct.objects.select_related('site').all()
    serializer_class = ScrapedProductSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['site', 'category', 'on_sale', 'in_stock']
    search_fields = ['name', 'description']
    ordering_fields = ['current_price', 'last_seen_at', 'created_at']
    ordering = ['-last_seen_at']

    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get only products on sale"""
        products = self.queryset.filter(on_sale=True, is_active=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def price_drops(self, request):
        """Get products with recent price drops"""
        # This would require more complex logic comparing with price history
        # For now, return products on sale
        products = self.queryset.filter(on_sale=True, is_active=True).order_by('-last_seen_at')[:20]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for a product"""
        product = self.get_object()
        history = PriceHistory.objects.filter(product=product).order_by('-recorded_at')[:30]
        serializer = PriceHistorySerializer(history, many=True)
        return Response(serializer.data)
