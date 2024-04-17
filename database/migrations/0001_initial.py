# Generated by Django 5.0 on 2024-04-16 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                ("title", models.CharField(max_length=255)),
                ("url", models.URLField(blank=True, max_length=1024, null=True)),
                ("date", models.CharField(blank=True, max_length=100, null=True)),
                ("main_topics", models.TextField(blank=True)),
                ("secondary_topics", models.TextField(blank=True)),
                ("keywords", models.TextField(blank=True)),
                ("summary", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Company",
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
                ("url", models.URLField(max_length=1024)),
                ("summary", models.TextField()),
                ("products_services", models.JSONField(default=dict)),
                ("strengths", models.JSONField(default=list)),
                ("keywords", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="User",
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
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="last name"
                    ),
                ),
                (
                    "company_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="company name"
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=100, null=True, verbose_name="title"),
                ),
                (
                    "company_url",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="company url",
                    ),
                ),
                (
                    "linkedin_url",
                    models.URLField(blank=True, null=True, verbose_name="linkedin url"),
                ),
                (
                    "youtube_url",
                    models.URLField(blank=True, null=True, verbose_name="youtube url"),
                ),
                (
                    "password",
                    models.CharField(
                        default="my_default_password",
                        max_length=128,
                        verbose_name="password",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                (
                    "is_staff",
                    models.BooleanField(default=False, verbose_name="staff status"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]