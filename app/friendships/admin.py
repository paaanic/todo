from django.contrib import admin

from .models import Friend, FriendshipRequest


class FriendshipRequestAdmin(admin.ModelAdmin):
    model = FriendshipRequest
    raw_id_fields = ['from_user', 'to_user']
    readonly_fields = ['create_date']


class FriendAdmin(admin.ModelAdmin):
    model = Friend
    raw_id_fields = ['from_user', 'to_user']
    readonly_fields = ['create_date']


admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
