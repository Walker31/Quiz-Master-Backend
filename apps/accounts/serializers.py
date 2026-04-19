from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Batch


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'avatar', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2',
                  'first_name', 'last_name', 'phone', 'role']

    def validate_role(self, value):
        # Students self-register; admins must be created by a superadmin
        if value in ('ADMIN', 'SUPERADMIN'):
            raise serializers.ValidationError(
                "Cannot self-register as Admin or Superadmin."
            )
        return value

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({'password2': "Passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data['user'] = user
        return data


class TokenPairSerializer(serializers.Serializer):
    """Returns access + refresh tokens alongside user info."""
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = UserSerializer(read_only=True)

    @staticmethod
    def get_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }


class BatchSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Batch
        fields = ['id', 'name', 'admin', 'students', 'student_count',
                  'start_date', 'end_date', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_student_count(self, obj):
        return obj.students.count()


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """Superadmin-only: create an admin or student account with any role."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'phone', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
