from django.contrib import admin

from .models import Task, TaskNotification, TaskShare


class TaskNotificationInline(admin.StackedInline):
    model = TaskNotification
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskNotificationInline]
    readonly_fields = ['create_date']


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskNotification)
admin.site.register(TaskShare)
