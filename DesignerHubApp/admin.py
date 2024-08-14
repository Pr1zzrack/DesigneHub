from django.contrib import admin
from .models import *


class UserSocialNetworkLinkInline(admin.TabularInline):
    model = UserSocialNetworkLink
    extra = 1

class UserContactDataInline(admin.TabularInline):
    model = UserContactData
    extra = 1

class UserProfileAdmin(admin.ModelAdmin):
    inlines = [UserSocialNetworkLinkInline, UserContactDataInline]

class DesignerWorkAdmin(admin.ModelAdmin):
    exclude = ('views', 'likes',)

admin.site.register(DesignerWork, DesignerWorkAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserBalance)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(CustomUser)
admin.site.register(Chat)
admin.site.register(Message)
