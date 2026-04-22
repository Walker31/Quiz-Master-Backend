from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsAdmin, IsSuperAdmin
from .models import User, Batch
from .serializers import (
    RegisterSerializer, LoginSerializer, TokenPairSerializer,
    UserSerializer, BatchSerializer, AdminCreateUserSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(TokenPairSerializer.get_tokens(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(f"DEBUG: Login attempt with data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Login validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        user = serializer.validated_data['user']
        print(f"DEBUG: Login successful for user: {user.username}")
        return Response(TokenPairSerializer.get_tokens(user))


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass  # already invalid — that's fine
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BatchViewSet(viewsets.ModelViewSet):
    """Admin manages batches; students can list batches they belong to."""
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Batch.objects.filter(admin=user)
        return user.batches.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    @action(detail=True, methods=['post'], url_path='add-student')
    def add_student(self, request, pk=None):
        batch = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(pk=student_id, role='STUDENT')
            batch.students.add(student)
            return Response({'detail': f'{student.username} added to batch.'})
        except User.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='remove-student')
    def remove_student(self, request, pk=None):
        batch = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(pk=student_id, role='STUDENT')
            batch.students.remove(student)
            return Response({'detail': f'{student.username} removed from batch.'})
        except User.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserViewSet(viewsets.ModelViewSet):
    """Superadmin: manage all users; Admin: manage their own students."""
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin:
            return User.objects.all().order_by('-date_joined')
        # Admin sees only students in their batches
        return User.objects.filter(
            batches__admin=user, role='STUDENT'
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateUserSerializer
        return UserSerializer
