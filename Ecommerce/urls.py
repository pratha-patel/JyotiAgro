from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from .views import *

app_name = 'Ecommerce'

urlpatterns = [
    path('home/',home,name='home'),

    path('',homepage,name='homepage'),
    path('product_list/<int:category_id>/', product_list, name='product_list'),
    path('product_view/<int:product_id>/',product_view,name='product_view'),
    path('cart_view/',cart_view, name='cart_view'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    
    path('Ecommerce/increase_quantity/', increase_quantity, name='increase_quantity'),
    path('Ecommerce/decrease_quantity/', decrease_quantity, name='decrease_quantity'),
    path('Ecommerce/update_variant/<int:cart_item_id>/', update_variant, name='update_variant'),

    
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
   
    path('checkout/',checkout,name='checkout'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

