# Generated by Django 5.2.3 on 2025-06-20 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0002_rename_usersubscription_usertariff_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tariffplan",
            options={
                "ordering": ["price", "title"],
                "verbose_name": "Tariff Plan",
                "verbose_name_plural": "Tariff Plans",
            },
        ),
        migrations.RemoveIndex(
            model_name="tariffplan",
            name="billing_tar_name_d350cb_idx",
        ),
        migrations.RenameField(
            model_name="tariffplan",
            old_name="name",
            new_name="title",
        ),
        migrations.AddIndex(
            model_name="tariffplan",
            index=models.Index(fields=["title"], name="billing_tar_title_42f2a4_idx"),
        ),
    ]
