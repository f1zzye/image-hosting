# Generated manually for expiration_notification_sent field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_usertariff_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertariff',
            name='expiration_notification_sent',
            field=models.BooleanField(
                default=False,
                help_text='Whether expiration notification email has been sent',
                verbose_name='expiration notification sent'
            ),
        ),
    ]