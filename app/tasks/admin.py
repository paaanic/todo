from django.contrib import admin

from .models import Task, TaskShare, TaskNotification


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ['create_date']


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskShare)
admin.site.register(TaskNotification)
