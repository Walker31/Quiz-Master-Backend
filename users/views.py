from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignInSerializer, SignUpSerializer, UserSerializer


class SignUpView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = SignUpSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		refresh = RefreshToken.for_user(user)
		return Response(
			{
				'user': UserSerializer(user).data,
				'tokens': {
					'refresh': str(refresh),
					'access': str(refresh.access_token),
				},
			},
			status=status.HTTP_201_CREATED,
		)


class SignInView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = SignInSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data['user']

		refresh = RefreshToken.for_user(user)
		return Response(
			{
				'user': UserSerializer(user).data,
				'tokens': {
					'refresh': str(refresh),
					'access': str(refresh.access_token),
				},
			},
			status=status.HTTP_200_OK,
		)


class MeView(APIView):
	def get(self, request):
		return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
