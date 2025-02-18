# Generated by Django 5.1.5 on 2025-02-04 14:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('membership', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('brand_id', models.AutoField(primary_key=True, serialize=False)),
                ('brand_name', models.CharField(max_length=100)),
                ('create_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Brand',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=100)),
                ('category_image', models.ImageField(upload_to='media/products/')),
                ('create_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'Category',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('city_id', models.AutoField(primary_key=True, serialize=False)),
                ('city_name', models.CharField(max_length=100)),
                ('create_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'City',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Cart',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_user_type', models.CharField(choices=[('member', 'Member'), ('non-member', 'Non-member')], default='member', max_length=50)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('discounted_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='pending', max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('delivery_charges', models.DecimalField(decimal_places=2, max_digits=5)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.city')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Order',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_mode', models.CharField(choices=[('cash', 'Cash'), ('online', 'Online')], default='cash', max_length=50)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=100)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('payment_date', models.DateTimeField(auto_now=True)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='membership.user_membership')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.order')),
            ],
            options={
                'db_table': 'Payment',
            },
        ),
        migrations.CreateModel(
            name='Pincode',
            fields=[
                ('pincode_id', models.AutoField(primary_key=True, serialize=False)),
                ('area_pincode', models.CharField(max_length=10, unique=True)),
                ('delivery_charges', models.DecimalField(decimal_places=2, default=50.0, max_digits=5)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.city')),
            ],
            options={
                'db_table': 'Pincode',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='pincode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.pincode'),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('product_image', models.ImageField(upload_to='media/products/')),
                ('min_qty', models.IntegerField(default=1)),
                ('max_qty', models.IntegerField(default=5)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.category')),
            ],
            options={
                'db_table': 'Product',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('feedback_id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.TextField(max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.product')),
            ],
            options={
                'db_table': 'Feedback',
            },
        ),
        migrations.CreateModel(
            name='ProductBatch',
            fields=[
                ('batch_id', models.AutoField(primary_key=True, serialize=False)),
                ('manufacture_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('batch_code', models.CharField(max_length=100, unique=True)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.product')),
            ],
            options={
                'db_table': 'ProductBatch',
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('inventory_id', models.AutoField(primary_key=True, serialize=False)),
                ('quatity', models.IntegerField(default=0)),
                ('purchase_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('sales_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productbatch')),
            ],
            options={
                'db_table': 'Inventory',
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('variant_id', models.AutoField(primary_key=True, serialize=False)),
                ('units', models.CharField(max_length=50)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.brand')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.product')),
            ],
            options={
                'db_table': 'ProductVariant',
            },
        ),
        migrations.AddField(
            model_name='productbatch',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productvariant'),
        ),
        migrations.CreateModel(
            name='Order_Item',
            fields=[
                ('order_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('create_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.order')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productbatch')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productvariant')),
            ],
            options={
                'db_table': 'OrderItem',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.IntegerField()),
                ('review', models.CharField(max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('wishlist_id', models.AutoField(primary_key=True, serialize=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Wishlist',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cart_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.cart')),
                ('product_batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productbatch')),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productvariant')),
            ],
            options={
                'db_table': 'CartItem',
                'unique_together': {('cart', 'product_batch', 'product_variant')},
            },
        ),
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product_batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productbatch')),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.productvariant')),
                ('wishlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.wishlist')),
            ],
            options={
                'db_table': 'WishlistItem',
                'unique_together': {('wishlist', 'product_batch', 'product_variant')},
            },
        ),
    ]
