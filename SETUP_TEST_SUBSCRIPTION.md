# Setup Test Subscription Management Command

## Overview
The `setup_test_subscription` management command is designed to set up a test Premium subscription for testing the Celery email notification system for expiring subscriptions.

## Usage
```bash
python manage.py setup_test_subscription
```

## What it does
1. **Finds user `huilo22`** - Looks up the user by username
2. **Sets up Premium subscription** - Creates or updates the user's subscription to Premium plan
3. **Sets 3-day expiration** - Sets `expires_at` to exactly 3 days from now
4. **Activates subscription** - Sets `is_active=True`
5. **Resets notification flag** - Sets `expiration_notification_sent=False`
6. **Displays verification** - Shows comprehensive subscription details

## Requirements
- User `huilo22` must exist in the database
- The command will create a Premium plan if it doesn't exist

## Error Handling
- **User not found**: Clear error message if `huilo22` doesn't exist
- **General errors**: Comprehensive error reporting for any issues

## Premium Plan Features
The command creates/uses a Premium plan with:
- 200px thumbnails: ✓
- 400px thumbnails: ✓
- Original photo access: ✓
- Binary links: ✓
- Price: $9.99

## Output Example
```
✓ Found user: huilo22 (huilo22@example.com)
✓ Using existing Premium tariff plan
✓ Updated existing user tariff

============================================================
SUBSCRIPTION DETAILS VERIFICATION
============================================================
User: huilo22 (Test User)
Email: huilo22@example.com
Plan: Premium
Price: $9.99
Active: True
Expires at: 2025-07-11 14:03:49 UTC
Days until expiration: 2
Expiration notification sent: False
Created at: 2025-07-08 14:03:49 UTC
Updated at: 2025-07-08 14:03:49 UTC

Plan Features:
  - 200px thumbnail: ✓
  - 400px thumbnail: ✓
  - Original photo access: ✓
  - Binary links: ✓
============================================================
✓ Test subscription setup completed successfully!
Ready for Celery email notification system testing.
```

## Database Changes
The command also adds the `expiration_notification_sent` field to the `UserTariff` model if not already present. This field is used by the notification system to track whether an expiration email has been sent.

## Related Files
- `/src/billing/management/commands/setup_test_subscription.py` - The command implementation
- `/src/billing/models.py` - Updated with `expiration_notification_sent` field
- `/src/billing/migrations/0007_usertariff_expiration_notification_sent.py` - Database migration