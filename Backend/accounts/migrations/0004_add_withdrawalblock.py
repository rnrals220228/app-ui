from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_is_warning_active_user_last_score_updated_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WithdrawalBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(
                    max_length=11,
                    db_index=True,
                    validators=[
                        django.core.validators.RegexValidator(
                            regex=r"^010[0-9]{8}$",
                            message="전화번호는 하이픈 없이 01012341234 형식이어야 합니다.",
                        )
                    ],
                )),
                ("blocked_until", models.DateTimeField()),
                ("trust_score_at_withdrawal", models.DecimalField(
                    max_digits=3,
                    decimal_places=1,
                    validators=[
                        django.core.validators.MinValueValidator(Decimal("0.0")),
                        django.core.validators.MaxValueValidator(Decimal("99.9")),
                    ],
                )),
                ("reason", models.CharField(max_length=100)),
                ("status", models.CharField(
                    max_length=20,
                    choices=[
                        ("ACTIVE", "ACTIVE"),
                        ("EXPIRED", "EXPIRED"),
                        ("RELEASED", "RELEASED"),
                    ],
                    default="ACTIVE",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("withdrawn_user", models.ForeignKey(
                    to=settings.AUTH_USER_MODEL,
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    blank=True,
                    related_name="withdrawal_blocks",
                )),
            ],
        ),
        migrations.AddIndex(
            model_name="withdrawalblock",
            index=models.Index(
                fields=["phone_number", "status"],
                name="accounts_wi_phone_n_1e2b68_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="withdrawalblock",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("trust_score_at_withdrawal__gte", 0.0),
                    ("trust_score_at_withdrawal__lte", 99.9),
                ),
                name="accounts_withdrawalblock_trust_score_range",
            ),
        ),
    ]