from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles the validation of registration data (username, email, password)
    and the creation of a new user instance.
    """
    confirmed_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        """
        Validates the registration data.

        Checks if:
        1. The password and confirmed_password match.
        2. The email address is not already registered.

        Args:
            data (dict): The raw data to validate.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If passwords don't match or email exists.
        """
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError({"password": "The passwords do not match."})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "this email is already in use."})
            
        return data

    def create(self, validated_data):
        """
        Creates a new user instance.

        Removes the 'confirmed_password' field before creating the user
        using the UserManager's create_user method to ensure password hashing.

        Args:
            validated_data (dict): The validated data from the serializer.

        Returns:
            User: The newly created user instance.
        """
        validated_data.pop('confirmed_password')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates that both username and password are provided in the request.
    Actual authentication happens in the view.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)