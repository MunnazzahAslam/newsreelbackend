from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from users.models import PhoneVerification

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'is_top_rated', 'is_verified_phone_number')
    readonly_fields = ('posts', 'own_reviews', 'reviews', 'comments', 'subscribers', 'rating', 'ethics', 'trust',
                       'accuracy', 'fairness', 'contribution', 'expertise')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('email', 'phone_number', 'avatar', 'avatar_thumbnail', 'facebook', 'twitter', 'linkedin',
                       'bio', 'is_top_rated', 'is_verified_phone_number')}),
        (_('Statistics'), {
            'fields': ('posts', 'reviews', 'comments', 'subscribers', 'rating', 'ethics', 'trust', 'accuracy',
                       'fairness', 'contribution', 'expertise',),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone_number', 'password1', 'password2'),
        }),
    )


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    pass
