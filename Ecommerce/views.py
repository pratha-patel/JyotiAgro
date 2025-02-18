
from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Ecommerce.models import *
from membership.models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg
from datetime import date
from decimal import Decimal
import json




def is_admin_user(user):
    return user.is_authenticated and user.is_staff  # Example function

def home(request):
    return render(request, 'Ecommerce/base.html')

def checkout(request):
    return render(request, 'Ecommerce/checkout_page.html')


def homepage(request):
    categories = Category.objects.all()  # Get all categories
    category_data = [
        {
            'category_id': category.category_id,
            'category_name': category.category_name.capitalize(),
            'category_image': category.category_image.url if category.category_image else None,
        }
        for category in categories
    ]

    products = Product.objects.all()
    product_data = []

    # Default empty cart_product_ids (for non-logged-in users)
    cart_product_ids = []

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        inventory = Inventory.objects.filter(batch__variant=variant).first() if variant else None
        sales_price = inventory.sales_price if inventory else None
        rating = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']

        product_data.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_image': product.product_image.url if product.product_image else '/static/images/default-product.jpg',
            'sales_price': sales_price if sales_price is not None else "N/A",
            'rating': rating if rating is not None else 0
        })

    return render(request, "Ecommerce/homepage.html", {
        'categories': category_data,
        'product_data': product_data,
        'cart_product_ids': cart_product_ids,  # ✅ Pass this to the template
    })


@login_required
def product_list(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    products = Product.objects.filter(category=category)

    product_data = []
    cart_product_ids = []  # Default empty cart for unauthenticated users

    # Check if the user is logged in, then get cart details
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

    for product in products:
        variant = ProductVariant.objects.filter(product=product).first()
        inventory = Inventory.objects.filter(batch__variant=variant).first() if variant else None
        sales_price = inventory.sales_price if inventory else None

        # Get average rating
        rating = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

        product_data.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_image': product.product_image.url if product.product_image else None,
            'sales_price': sales_price,
            'rating': rating,
        })

    context = {
        'category_name': category.category_name,
        'products': product_data,
        'cart_product_ids': cart_product_ids,  # ✅ Add this for the cart check in the template
    }

    return render(request, 'Ecommerce/product_list_page.html', context)



@login_required
def product_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    print(f"Product ID: {product.product_id}")  # Debugging
    # Fetch variants and related brands
    variants = list(ProductVariant.objects.filter(product=product).select_related('brand'))

    # Fetch inventory related to those variants
    inventories = Inventory.objects.filter(batch__variant__in=variants).select_related('batch__variant')

    # Build variant prices dictionary
    variant_prices = {
        str(inventory.batch.variant.variant_id): float(inventory.sales_price) 
        for inventory in inventories
    }

    # Get the first available price, else "N/A"
    first_price = next((price for price in variant_prices.values() if price is not None), "N/A")

    # Calculate average rating
    rating_data = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))
    rating = round(rating_data['avg_rating'], 1) if rating_data['avg_rating'] is not None else 0

    # Fetch reviews in descending order
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    # ✅ Get cart product IDs
    cart_product_ids = []
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

    # ✅ Handle review submission
    if request.method == "POST":
        rating_value = request.POST.get('rating') 
        review_text = request.POST.get('comment') 

        if rating_value and review_text:  # Ensure both fields are filled
            Review.objects.create(
                user=request.user,
                product=product,
                rating=int(rating_value),  # Convert to integer
                review=review_text.strip()  # Trim spaces
            )
            return redirect('Ecommerce:product_view', product_id=product.product_id)

    # Prepare product data
    product_data = {
        'product_id': product.product_id,
        'product_name': product.product_name,
        'product_image': product.product_image.url if product.product_image else "/static/images/no_image.jpg",
        'description': product.description,
        'rating': rating,
        'first_price': first_price,
    }
    print("✅ Variant Prices JSON:", json.dumps(variant_prices, ensure_ascii=False)) 
    context = {
        'product': product_data,
        'stars_range': range(1, 6),
        'reviews': reviews,
        'variants': variants,
        'cart_product_ids': cart_product_ids,  # ✅ Add cart products for button logic
    }

    return render(request, 'Ecommerce/product_view.html', {**context,'variant_prices': json.dumps(variant_prices)})




# View Cart


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Get the user's cart
    cart_items = CartItem.objects.filter(cart=cart).select_related(  # ✅ Filter by user's cart
        "product_variant", "product_variant__product", "product_batch"
    ).prefetch_related("product_batch__inventory_set")

    # Store variant prices
    variant_prices = {}

    cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

    grand_total = sum(item.total_price for item in cart_items)  # Calculate grand total

    for item in cart_items:
        inventory = Inventory.objects.filter(batch=item.product_batch).first()
        item.product_variants = ProductVariant.objects.filter(product=item.product_variant.product)
        item.sales_price = float(inventory.sales_price) if inventory else 0  # Convert Decimal to float
        item.variant_price = inventory.sales_price if inventory else 0  # Handle missing inventory

        # Get all variants of the same product
        item.product_variants = ProductVariant.objects.filter(product=item.product_variant.product)

        # Store prices for each variant
        for variant in item.product_variants:
            inventory_variant = Inventory.objects.filter(batch__variant=variant).first()
            variant_prices[str(variant.variant_id)] = float(inventory_variant.sales_price) if inventory_variant else 0

    context = {
        "cart_items": cart_items,
        "cart_product_ids": cart_product_ids,
        "variant_prices": variant_prices,
        "grand_total": grand_total,
    }

    return render(request, "Ecommerce/cart.html", context)






@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    # Get first available variant and batch
    variant = ProductVariant.objects.filter(product=product).first()
    batch = ProductBatch.objects.filter(product=product, variant=variant).first()

    if not variant or not batch:
        return JsonResponse({"success": False, "message": "Product variant or batch not found"})

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the item already exists in the cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_batch=batch,
        product_variant=variant,
        defaults={'quantity': 1}  # Default quantity when adding for the first time
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("Ecommerce:homepage")
    # return JsonResponse({"success": True, "message": "Product added to cart successfully!"})







# Remove from Cart
@login_required
def remove_from_cart(request,item_id):
    cart_item = get_object_or_404(CartItem, cart__user=request.user, cart_item_id=item_id)
    cart_item.delete()

    return redirect('Ecommerce:cart_view')




@login_required
def increase_quantity(request):
    """Increases the quantity of a cart item, updates the price, and stores in DB."""

    if request.method == "POST":
        item_id = request.POST.get('item_id')

        if not item_id:
            return redirect("Ecommerce:cart_view")

        cart_item = get_object_or_404(CartItem, cart_item_id=item_id, cart__user=request.user)
        
        
        product = cart_item.product_variant.product  

        if cart_item.quantity < product.max_qty:
            cart_item.quantity += 1
            cart_item.save()


    return redirect('Ecommerce:cart_view')



@login_required
def decrease_quantity(request):
    """Decreases the quantity of a cart item, updates the price, and stores in DB."""

    if request.method == "POST":
        item_id = request.POST.get('item_id')

        if not item_id:
            return redirect("Ecommerce:cart_view")

        cart_item = get_object_or_404(CartItem, cart_item_id=item_id, cart__user=request.user)

        product = cart_item.product_variant.product  

        if cart_item.quantity > product.min_qty:
            cart_item.quantity -= 1
            cart_item.save()

        

    return redirect('Ecommerce:cart_view')



def update_variant(request, cart_item_id):
    """Handles variant selection and updates the cart item."""
    
    if request.method == "POST":
        variant_id = request.POST.get("variant_id")
        
        if not variant_id:
            return redirect("Ecommerce:cart_view")  # Redirect if no variant selected
        
        # Get the cart item
        cart_item = get_object_or_404(CartItem, cart_item_id=cart_item_id, cart__user=request.user)

        # Get the selected variant
        new_variant = get_object_or_404(ProductVariant, variant_id=variant_id)

        # Get the corresponding batch
        new_batch = get_object_or_404(ProductBatch, variant=new_variant)

        # Fetch the inventory record for the selected variant
        inventory = Inventory.objects.filter(batch__variant=new_variant).first()
        
        if inventory:
            # Update the cart item with the new variant and price
            cart_item.product_variant = new_variant
            cart_item.product_batch = new_batch
            cart_item.save()
        else:
            print("No inventory found for this variant")  # Debugging

    return redirect("Ecommerce:cart_view")  # Reload the cart page to reflect changes


# checkout


# @login_required
# def checkout(request):
#     cart = Cart.objects.get(user=request.user)  # Get the user's cart
#     cart_items = cart.cartitem_set.all()  # Fetch all items in the cart
#     cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

#     # Check if the user has an active membership
#     user_membership = User_membership.objects.filter(
#         user=request.user, 
#         status=True, 
#         membership_end_date__gte=date.today()  # Ensure the membership is active
#     ).select_related('plan').first()

#     membership_discount = Decimal(0)  # Ensure it's Decimal
#     membership_plan_name = None
#     is_member = False

#     if user_membership:
#         membership_discount = Decimal(user_membership.plan.discount_rate)  # Convert to Decimal
#         membership_plan_name = user_membership.plan.plan_name
#         is_member = True

#     for item in cart_items:
#         inventory = Inventory.objects.filter(batch=item.product_batch).first()
#         item.product_variants = ProductVariant.objects.filter(product=item.product_variant.product)
#         item.sales_price = Decimal(inventory.sales_price) if inventory else Decimal(0)  # ✅ Convert to Decimal

#     # Calculate grand total using Decimal
#     grand_total = sum(Decimal(item.total_price) for item in cart_items)  # ✅ Keep as Decimal

#     # Apply membership discount
#     discount_amount = (grand_total * membership_discount / Decimal(100)) if user_membership else Decimal(0)

#     total_after_discount = grand_total - discount_amount  # ✅ Decimal subtraction

#     # Get Delivery Charge from Database
#     registered_pincode = str(request.user.pincode)  # Assuming pincode is stored in User model
#     delivery_charge = Decimal(0) if is_member else Decimal(get_delivery_charge(registered_pincode))

#     # Final Total with Delivery Charge
#     final_total = total_after_discount + delivery_charge  # ✅ Ensure both are Decimal

#     # Store variant prices as Decimal
#     variant_prices = {
#         str(variant.variant_id): Decimal(Inventory.objects.filter(batch__variant=variant).first().sales_price)  
#         if Inventory.objects.filter(batch__variant=variant).exists() else Decimal(0)
#         for item in cart_items for variant in item.product_variants
#     }

#     return render(request, "Ecommerce/checkout_page.html", {
#         "cart_items": cart_items,
#         "cart_product_ids": cart_product_ids,
#         "variant_prices": json.dumps({k: str(v) for k, v in variant_prices.items()}),  # Convert Decimal to string for JSON
#         "grand_total": grand_total,
#         "discount_amount": discount_amount,  
#         "total_after_discount": total_after_discount,  
#         "is_member": is_member,  
#         "membership_plan_name": membership_plan_name,  
#         "delivery_charge": delivery_charge,  # Pass delivery charge to template
#         "final_total": final_total,  # Final amount after discount and delivery charge
#     })



# def get_delivery_charge(pincode):
#     """Fetches delivery charge from the database using the Pincode model."""
#     try:
#         pincode_instance = Pincode.objects.get(area_pincode=pincode)
#         return float(pincode_instance.delivery_charges)  # Convert Decimal to float
#     except Pincode.DoesNotExist:
#         return 60  # Default charge if pincode not found




@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)  
    cart_items = cart.cartitem_set.all()  
    cart_product_ids = list(cart_items.values_list("product_variant__product__product_id", flat=True))

    # Fetch cities
    cities = City.objects.all()

    selected_city_id = request.POST.get("city")  # Get selected city from the form
    selected_pincode_id = request.POST.get("pincode")  # Get selected pincode from the form
    pincodes = Pincode.objects.filter(city_id=selected_city_id) if selected_city_id else []

    # Check for active membership
    user_membership = User_membership.objects.filter(
        user=request.user, 
        status=True, 
        membership_end_date__gte=date.today()
    ).select_related('plan').first()

    membership_discount = Decimal(0)
    membership_plan_name = None
    is_member = False

    if user_membership:
        membership_discount = Decimal(user_membership.plan.discount_rate)
        membership_plan_name = user_membership.plan.plan_name
        is_member = True

    for item in cart_items:
        inventory = Inventory.objects.filter(batch=item.product_batch).first()
        item.product_variants = ProductVariant.objects.filter(product=item.product_variant.product)
        item.sales_price = Decimal(inventory.sales_price) if inventory else Decimal(0)

    # Calculate grand total
    grand_total = sum(Decimal(item.total_price) for item in cart_items)
    discount_amount = (grand_total * membership_discount / Decimal(100)) if user_membership else Decimal(0)
    total_after_discount = grand_total - discount_amount

    # Get delivery charge
    delivery_charge = Decimal(0)
    if selected_pincode_id:
        delivery_charge = Decimal(get_delivery_charge(selected_pincode_id))

    final_total = total_after_discount + delivery_charge

    # Store variant prices
    variant_prices = {
        str(variant.variant_id): Decimal(Inventory.objects.filter(batch__variant=variant).first().sales_price)  
        if Inventory.objects.filter(batch__variant=variant).exists() else Decimal(0)
        for item in cart_items for variant in item.product_variants
    }

    context = {
        "cart_items": cart_items,
        "cart_product_ids": cart_product_ids,
        "variant_prices": json.dumps({k: str(v) for k, v in variant_prices.items()}),
        "grand_total": grand_total,
        "discount_amount": discount_amount,
        "total_after_discount": total_after_discount,
        "is_member": is_member,
        "membership_plan_name": membership_plan_name,
        "delivery_charge": delivery_charge,
        "final_total": final_total,
        "cities": cities,
        "pincodes": pincodes,
        "selected_city_id": selected_city_id,
        "selected_pincode_id": selected_pincode_id,
    }

    return render(request, "Ecommerce/checkout_page.html", context)

def get_delivery_charge(pincode_id):
    """Fetches delivery charge from the database using the Pincode model."""
    try:
        pincode_instance = Pincode.objects.get(pincode_id=pincode_id)
        return float(pincode_instance.delivery_charges)  
    except Pincode.DoesNotExist:
        return 0


