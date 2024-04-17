from django.db import models
import json
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=100, null=True)
    last_name = models.CharField(_('last name'), max_length=100, null=True)
    company_name = models.CharField(_('company name'), max_length=100, null=True)
    title = models.CharField(_('title'), max_length=100, null=True)
    company_url = models.CharField(_('company url'), max_length=100, null=True, blank=True)
    linkedin_url = models.URLField(_('linkedin url'), null=True, blank=True)
    youtube_url = models.URLField(_('youtube url'), null=True, blank=True)
    password = models.CharField(_('password'), max_length=128, default='my_default_password')
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Company(models.Model):
    url = models.URLField(max_length=1024)
    summary = models.TextField()
    products_services = models.JSONField(default=dict)
    strengths = models.JSONField(default=list)
    keywords = models.JSONField(default=list)  # Assurez-vous que ce champ peut stocker une liste.
    company_specific_keywords = models.JSONField(default=list)  # Ajouté pour stocker les mots clés spécifiques.

    def __str__(self):
        return f"{self.url} - {self.summary[:50]}..."

    def save(self, *args, **kwargs):
        if isinstance(self.products_services, str):
            self.products_services = json.loads(self.products_services)
        if isinstance(self.strengths, str):
            self.strengths = json.loads(self.strengths)
        if isinstance(self.keywords, str):
            self.keywords = json.loads(self.keywords)
        if isinstance(self.company_specific_keywords, str):
            self.company_specific_keywords = json.loads(self.company_specific_keywords)
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=255)  # Titre de l'article
    url = models.URLField(max_length=1024, blank=True, null=True)  # Lien vers l'article, peut être non fourni
    date = models.CharField(max_length=100, blank=True, null=True)  # Date de publication, peut être non fournie
    main_topics = models.TextField(blank=True)  # Sujets principaux
    secondary_topics = models.TextField(blank=True)  # Sujets secondaires
    keywords = models.TextField(blank=True)  # Mots clés associés à l'article
    summary = models.TextField()  # Résumé de l'article

    def __str__(self):
        return f"{self.title} - {self.url}"