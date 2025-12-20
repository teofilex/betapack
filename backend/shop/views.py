from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from django.db import models
from .models import (
    Category, Subcategory, Product, ProductVariant,
    ProductImage, Order, OrderItem, ContactMessage
)
from .serializers import (
    CategorySerializer, SubcategorySerializer, ProductSerializer,
    ProductVariantSerializer, ProductImageSerializer,
    OrderSerializer, OrderCreateSerializer, ContactMessageSerializer
)


# User info endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
    })


# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]


# Subcategory ViewSet
class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('images', 'variants').select_related('category', 'subcategory')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


    def destroy(self, request, *args, **kwargs):
        # Dozvoli brisanje proizvoda bez provere narudžbina
        # OrderItem će imati product=None zbog SET_NULL, ali će zadržati product_name za istorijat
        return super().destroy(request, *args, **kwargs)


# ProductVariant ViewSet
class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = ProductVariant.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        # Dozvoli brisanje varijante bez provere narudžbina
        # OrderItem će imati variant=None zbog SET_NULL, ali će zadržati variant_name za istorijat
        return super().destroy(request, *args, **kwargs)


# ProductImage ViewSet
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = ProductImage.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


# Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        # Samo admini mogu videti sve narudžbine
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        # CREATE je javno dostupan (korisnici kreiraju narudžbine)
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Smanji količinu na stanju za svaku stavku narudžbine
        # Ovo je opciono - ako dođe do greške, ne prekidaj kreiranje narudžbine
        try:
            for item in order.items.all():
                # Ako postoji varijanta, smanji količinu varijante
                if item.variant_id is not None:
                    try:
                        variant = ProductVariant.objects.filter(id=item.variant_id).first()
                        if variant and hasattr(variant, 'stock_quantity') and variant.stock_quantity is not None and variant.stock_quantity > 0:
                            variant.stock_quantity = max(0, variant.stock_quantity - item.quantity)
                            variant.save(update_fields=['stock_quantity'])
                    except Exception:
                        pass
                
                # Ako nema varijante ili varijanta nema ograničenu količinu, smanji količinu proizvoda
                if item.product_id is not None:
                    try:
                        product = Product.objects.filter(id=item.product_id).first()
                        if product and hasattr(product, 'stock_quantity') and product.stock_quantity is not None and product.stock_quantity > 0:
                            product.stock_quantity = max(0, product.stock_quantity - item.quantity)
                            product.save(update_fields=['stock_quantity'])
                    except Exception:
                        pass
        except Exception as e:
            # Loguj grešku ali ne prekidaj kreiranje narudžbine
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating stock quantities: {str(e)}", exc_info=True)

        # Pošalji email notifikaciju vlasniku (privremeno isključeno dok se ne podesi SMTP)
        # self.send_order_notification(order)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    def send_order_notification(self, order):
        """Pošalji email notifikaciju vlasniku o novoj narudžbini"""
        try:
            subject = f'Nova narudžbina #{order.id}'
            message = f"""
Nova narudžbina je primljena!

Narudžbina: #{order.id}
Kupac: {order.customer_name}
Telefon: {order.customer_phone}
Email: {order.customer_email or 'Nije ostavljen'}
Ukupno: {order.total_amount} RSD

Stavke:
"""
            for item in order.items.all():
                variant_info = f" ({item.variant_name})" if item.variant_name else ""
                message += f"- {item.product_name}{variant_info} x{item.quantity} = {item.total_price} RSD\n"

            if order.notes:
                message += f"\nNapomena kupca: {order.notes}"

            if order.address and order.city:
                message += f"\nAdresa dostave: {order.address}, {order.city}"

            message += f"\n\n---\nProveri admin panel za više detalja."

            # Email za vlasnike iz settings
            recipient_list = settings.OWNER_EMAILS

            # Pošalji email preko Resend-a svakom primaocu
            from shop.email_utils import send_email_via_resend
            for recipient in recipient_list:
                send_email_via_resend(
                    subject=subject,
                    message=message,
                    recipient_email=recipient,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )

            order.email_sent = True
            order.save(update_fields=['email_sent'])

        except Exception as e:
            print(f"Email send error: {e}")

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Ažuriraj status narudžbine"""
        order = self.get_object()
        new_status = request.data.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'success', 'new_status': order.status})

        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )


# SSE endpoint za real-time notifikacije o novim orderima
from django.http import StreamingHttpResponse
import json
import time

def order_notifications_stream(request):
    """Server-Sent Events stream za notifikacije o novim orderima"""
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.tokens import UntypedToken
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Proveri autentifikaciju preko query parametra (token)
    token = request.GET.get('token')
    if not token:
        return StreamingHttpResponse('Unauthorized', status=401)
    
    try:
        # Validiraj token
        UntypedToken(token)
        from rest_framework_simplejwt.state import token_backend
        decoded_data = token_backend.decode(token, verify=True)
        user_id = decoded_data.get('user_id')
        user = User.objects.get(id=user_id)
        
        if not user or not user.is_staff:
            return StreamingHttpResponse('Unauthorized', status=401)
    except (InvalidToken, TokenError, User.DoesNotExist) as e:
        return StreamingHttpResponse('Unauthorized', status=401)
    
    def event_stream():
        last_order_id = None
        
        # Prvo pošalji trenutni broj ordera
        current_count = Order.objects.count()
        yield f"data: {json.dumps({'type': 'init', 'count': current_count})}\n\n"
        
        while True:
            try:
                # Proveri da li ima novih ordera
                if last_order_id:
                    new_orders = Order.objects.filter(id__gt=last_order_id).order_by('-id')
                else:
                    # Prvi put - uzmi poslednji order
                    last_order = Order.objects.order_by('-id').first()
                    if last_order:
                        last_order_id = last_order.id
                    new_orders = []
                
                if new_orders.exists():
                    for order in new_orders:
                        yield f"data: {json.dumps({'type': 'new_order', 'order_id': order.id})}\n\n"
                        last_order_id = order.id
                
                # Heartbeat svakih 5 sekundi
                yield f": heartbeat\n\n"
                time.sleep(5)
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                time.sleep(5)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_message(request):
    """
    Endpoint za prijem kontakt poruka
    """
    from .serializers import ContactMessageSerializer
    from .models import ContactMessage

    try:
        serializer = ContactMessageSerializer(data=request.data)

        if serializer.is_valid():
            # Sačuvaj poruku u bazu
            contact_msg = serializer.save()

            # Pokušaj da pošalješ email
            try:
                recipient_email = settings.CONTACT_EMAIL_RECIPIENT

                # Sastavi email
                subject = f'Nova kontakt poruka od {contact_msg.name}'

                message = f"""
Nova kontakt poruka sa sajta:

Ime: {contact_msg.name}
Email: {contact_msg.email or 'Nije naveden'}
Telefon: {contact_msg.phone}

Poruka:
{contact_msg.message}

---
Datum: {contact_msg.created_at.strftime('%d.%m.%Y %H:%M')}
                """

                # Pošalji email preko Resend-a
                from shop.email_utils import send_email_via_resend
                send_email_via_resend(
                    subject=subject,
                    message=message,
                    recipient_email=recipient_email,
                    from_email=settings.DEFAULT_FROM_EMAIL
                )
            except Exception as e:
                # Loguj grešku ali ne prekidaj - poruka je već sačuvana
                print(f"Email sending failed: {e}")

            return Response({
                'success': True,
                'message': 'Poruka uspešno poslata!'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Osiguraj da se uvek vraća pravilni response sa CORS headerima
        print(f"Error in contact_message view: {e}")
        return Response({
            'success': False,
            'message': 'Došlo je do greške prilikom slanja poruke. Molimo pokušajte ponovo.',
            'error': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ContactMessage ViewSet
class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        # Samo admini mogu videti poruke
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        # CREATE je javno dostupan (korisnici kreiraju poruke)
        return [permissions.AllowAny()]