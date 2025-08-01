# Generated by Django 5.2.3 on 2025-06-20 20:17

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0003_alter_tariffplan_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="tariffplan",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Tariff price",
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0.0)],
                verbose_name="price",
            ),
        ),
        migrations.AlterField(
            model_name="usertariff",
            name="is_active",
            field=models.BooleanField(
                default=True, help_text="Is the tariff active", verbose_name="is active"
            ),
        ),
        migrations.AlterField(
            model_name="usertariff",
            name="plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="billing.tariffplan",
                verbose_name="tariff plan",
            ),
        ),
        migrations.AlterField(
            model_name="usertariff",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tariff",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
    ]
