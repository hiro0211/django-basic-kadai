# Generated by Django 4.2.6 on 2023-10-13 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0004_product_img'),
    ]

    operations = [
        migrations.CreateModel(
            name='detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
