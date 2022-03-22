from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from tasks.models import Task

tasks = []
completed_tasks = []

def tasks_view(request):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted = False, completed = False)
    if search_term:
        tasks = Task.objects.filter(title__icontains = search_term)
    return render(request, "tasks.html", {"tasks":tasks})

def add_task_view(request):
    task_value = request.GET.get('task')
    Task(title = task_value).save()
    return HttpResponseRedirect("/tasks")

def delete_task_view(request, index):
    task_obj = Task.objects.filter(id=index)
    task_obj.update(deleted = True)
    return HttpResponseRedirect("/tasks")

def complete_task_view(request,index):
    Task.objects.filter(id=index).update(completed = True)
    return HttpResponseRedirect("/tasks")

def complete_list_view(request):
    completed_tasks = Task.objects.filter(completed = True)
    return render(request, "completed_tasks.html", {"tasks":completed_tasks})

def all_tasks_view(request):
    tasks = Task.objects.filter(deleted = False, completed = False)
    completed_tasks = Task.objects.filter(completed = True)

    return render(request, "all_tasks.html", {"tasks":tasks, "completed_tasks":completed_tasks})
