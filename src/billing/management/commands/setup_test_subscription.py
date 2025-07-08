from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from billing.models import TariffPlan, UserTariff

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up a test Premium subscription for user huilo22 that expires in 3 days'

    def handle(self, *args, **options):
        username = 'huilo22'

        try:
            # Find the user
            try:
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Found user: {user.username} ({user.email})')
                )
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist.')

            # Get or create Premium plan
            premium_plan, created = TariffPlan.objects.get_or_create(
                title='Premium',
                defaults={
                    'description': 'Premium subscription plan',
                    'price': 9.99,
                    'is_built_in': True,
                    'has_thumbnail_200px': True,
                    'has_thumbnail_400px': True,
                    'has_original_photo': True,
                    'has_binary_link': True,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS('✓ Created Premium tariff plan')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ Using existing Premium tariff plan')
                )

            # Set expiration date to exactly 3 days from now
            expires_at = timezone.now() + timedelta(days=3)

            # Get or create user tariff
            user_tariff, created = UserTariff.objects.get_or_create(
                user=user,
                defaults={
                    'plan': premium_plan,
                    'is_active': True,
                    'expires_at': expires_at,
                    'expiration_notification_sent': False,
                }
            )

            if not created:
                # Update existing tariff
                user_tariff.plan = premium_plan
                user_tariff.is_active = True
                user_tariff.expires_at = expires_at
                user_tariff.expiration_notification_sent = False
                user_tariff.paypal_subscription_id = None  # Reset payment info for test
                user_tariff.save()
                self.stdout.write(
                    self.style.SUCCESS('✓ Updated existing user tariff')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✓ Created new user tariff')
                )

            # Display subscription details for verification
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('SUBSCRIPTION DETAILS VERIFICATION'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'User: {user.username} ({user.get_full_name()})')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Plan: {user_tariff.plan.title}')
            self.stdout.write(f'Price: ${user_tariff.plan.price}')
            self.stdout.write(f'Active: {user_tariff.is_active}')
            self.stdout.write(f'Expires at: {user_tariff.expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")}')
            self.stdout.write(f'Days until expiration: {(user_tariff.expires_at - timezone.now()).days}')
            self.stdout.write(f'Expiration notification sent: {user_tariff.expiration_notification_sent}')
            self.stdout.write(f'Created at: {user_tariff.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}')
            self.stdout.write(f'Updated at: {user_tariff.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC")}')

            # Show plan features
            self.stdout.write('\nPlan Features:')
            self.stdout.write(f'  - 200px thumbnail: {"✓" if user_tariff.plan.has_thumbnail_200px else "✗"}')
            self.stdout.write(f'  - 400px thumbnail: {"✓" if user_tariff.plan.has_thumbnail_400px else "✗"}')
            self.stdout.write(f'  - Original photo access: {"✓" if user_tariff.plan.has_original_photo else "✗"}')
            self.stdout.write(f'  - Binary links: {"✓" if user_tariff.plan.has_binary_link else "✗"}')

            self.stdout.write('=' * 60)
            self.stdout.write(
                self.style.SUCCESS('✓ Test subscription setup completed successfully!')
            )
            self.stdout.write(
                self.style.WARNING('Ready for Celery email notification system testing.')
            )

        except Exception as e:
            raise CommandError(f'Error setting up test subscription: {str(e)}')