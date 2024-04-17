from rest_framework import serializers
from database.models import User
from database.models import UserSource, User, LinkedInPost
from database.models import Article
from rest_framework import serializers



## serializer pour l'API user creation ##

from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'company_name', 'title', 'company_url', 'linkedin_url', 'youtube_url', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        return user

## serializer pour l'API user_source creation ##

class UserSourceSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = UserSource
        fields = ['email', 'competitors', 'linkedin', 'references', 'youtube']

    def create(self, validated_data):
        user_email = validated_data.pop('email', None)
        if user_email:
            user, created = User.objects.get_or_create(email=user_email)
            validated_data['user'] = user
        user_source = UserSource.objects.create(**validated_data)
        return user_source
    


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'base_content', 'content', 'tone_of_voice', 'content_goal', 'user_comment', 'content_size', 'goals', 'email', 'product', 'description', 'Company_info', 'language', "ID_content"]


class TrendSerializer(serializers.Serializer):
    titre = serializers.CharField(max_length=300)
    base_content = serializers.CharField(max_length=1500)
    email = serializers.EmailField()
    Company_info = serializers.CharField(max_length=1500)


class TailorTrendSerializer(serializers.Serializer):
    titre = serializers.CharField(max_length=500)
    base_content = serializers.CharField(max_length=1500)
    email = serializers.EmailField()
    product = serializers.CharField(max_length=1500)
    Company_info = serializers.CharField(max_length=1500)
    description = serializers.CharField(max_length=3000)

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError('No active user found with the given credentials')

        data = super().validate(attrs)
        refresh = self.get_token(user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        # Ajoutez les informations supplémentaires que vous souhaitez inclure dans la réponse du token
        # Par exemple, nom d'utilisateur, rôles, etc.
        
        return data
    

class LinkedInPostSerializer(serializers.ModelSerializer):
        class Meta:
            model = LinkedInPost
            fields = '__all__'