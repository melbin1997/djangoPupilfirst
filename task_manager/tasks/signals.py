from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Task, TaskStatusChange

@receiver(pre_save, sender=Task)
def task_status_change(sender, instance, *args, **kwargs):
    # print(f'sender : {sender} \n instance : {instance} \n args : {args} \n kwargs : {kwargs} ')
    oldStatus = Task.objects.filter(id=instance.id).first().status
    if oldStatus != instance.status:
        TaskStatusChange(old_status=oldStatus, new_status=instance.status, task=instance).save()