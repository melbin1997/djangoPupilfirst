from django.contrib import admin

from tasks.models import Task, TaskStatusChange


admin.sites.site.register(Task)
admin.sites.site.register(TaskStatusChange)
