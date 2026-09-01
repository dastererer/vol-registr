import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FreeAgentApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=100)),
                ("message", models.TextField(max_length=1200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "New"),
                            ("CONTACTED", "Captain contacted"),
                            ("CLOSED", "Closed"),
                        ],
                        db_index=True,
                        default="NEW",
                        max_length=20,
                    ),
                ),
                ("email_sent", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="free_agent_applications",
                        to="tournament.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Free-agent application",
                "verbose_name_plural": "Free-agent applications",
                "db_table": "free_agent_applications",
                "ordering": ["-created_at"],
            },
        ),
    ]
