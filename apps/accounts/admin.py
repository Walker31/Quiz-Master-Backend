from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Batch


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for the custom User model.
    Extends Django's BaseUserAdmin with additional role-based fields.
    """
    list_display = ('username', 'email', 'role', 'is_verified', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Role-based Access', {'fields': ('role', 'is_verified')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Role-based Access', {'fields': ('role',)}),
    )
    
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    """
    Admin interface for Batch model.
    Displays batch details, associated students, and admin assignment.
    """
    list_display = ('name', 'code', 'admin', 'student_count', 'is_active', 'start_date')
    list_filter = ('is_active', 'start_date', 'admin')
    search_fields = ('name', 'code', 'admin__username')
    filter_horizontal = ('students',)
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'code')}),
        ('Admin Assignment', {'fields': ('admin',)}),
        ('Students', {'fields': ('students',)}),
        ('Duration', {'fields': ('start_date', 'end_date')}),
        ('Status', {'fields': ('is_active',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Number of Students'
