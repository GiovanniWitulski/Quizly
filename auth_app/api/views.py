from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegistrationSerializer

class RegisterView(APIView):
    """
    API View for user registration.
    
    Allows any user to create a new account.
    """
    permission_classes = [] 

    def post(self, request):
        """
        Creates a new user.

        Request Body:
            - username (str): Desired username.
            - email (str): Email address.
            - password (str): Password.
            - confirmed_password (str): Password confirmation.

        Returns:
            201: User created successfully.
            400: Validation errors (e.g., passwords do not match).
        """
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"}, 
                status=status.HTTP_201_CREATED
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    """
    API View for user login.
    
    Authenticates the user and sets JWT tokens (Access & Refresh) as HTTP-Only cookies.
    """
    permission_classes = []

    def post(self, request):
        """
        Logs the user in.

        Request Body:
            - username (str)
            - password (str)

        Returns:
            200: Login successful, cookies set.
            401: Invalid credentials.
            400: Malformed request.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                response = Response({
                    "detail": "Login successfully!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }, status=status.HTTP_200_OK)

                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    samesite='Lax',
                    secure=False,
                    max_age=30 * 60
                )

                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    samesite='Lax',
                    secure=False,
                    max_age=24 * 60 * 60 
                )

                return response
            
            else:
                return Response(
                    {"detail": "Invalid credentials."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    """
    API View for user logout.
    
    Blacklists the refresh token and deletes authentication cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Performs the logout.

        Expects the 'refresh_token' to be present in the cookies.

        Returns:
            200: Successfully logged out.
            500: Server error during blacklisting.
        """
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
        except TokenError:
            pass
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = Response({
            "detail": "Log-Out successfull! All Tokens will be deleted. Refresh token is now invalid."
        }, status=status.HTTP_200_OK)

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
    
class RefreshTokenView(APIView):
    """
    API View to refresh the access token.
    
    Reads the refresh token from the cookie and generates a new access token.
    """
    permission_classes = []

    def post(self, request):
        """
        Requests a new access token.

        Returns:
            200: New access token generated and set as cookie.
            401: Refresh token invalid or missing.
        """
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh Token ungültig oder fehlt."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({
                "detail": "Token refreshed",
                "access": access_token
            }, status=status.HTTP_200_OK)

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                samesite='Lax',
                secure=False,
                max_age=30 * 60 
            )

            return response
            
        except TokenError:
            return Response(
                {"detail": "Refresh Token ungültig oder fehlt."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )