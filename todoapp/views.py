import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Category
from .forms import TaskForm, CategoryForm
from datetime import timedelta
from django.utils import timezone



def calendar_view(request):
    tasks = Task.objects.all()
    categories = Category.objects.all()
    now = timezone.now()
    previous_tasks = Task.objects.filter(start_time__date=now.date()).order_by('-end_time')

    events = []
    for task in tasks:
        events.append({
            'id': task.id,
            'title': task.title,
            'start': task.start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': task.end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'color': task.color,
            'status': task.status,
        })
    return render(request, 'todo/calendar.html', {
        'events': json.dumps(events),
        'categories': categories,
        'previous_tasks': previous_tasks

    })

def task_update_calendar(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        task.status = status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'todo/task_list.html', {'tasks': tasks})

def task_create(request, start_time=None):
    now = timezone.now()
    previous_tasks = Task.objects.filter(start_time__date=now.date()).order_by('-end_time')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'pending'
            if not task.end_time:
                # task.duration = task.category.default_duration
                task.end_time = task.start_time + timedelta(minutes=task.duration)

            task.save()
            if task.repeat != 'none':
                create_repeated_tasks(task)
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = TaskForm(initial={'start_time': start_time})

    return render(request, 'todo/task_form.html', {'form': form, 'previous_tasks': previous_tasks})

def create_repeated_tasks(task):
    repeat_intervals = {
        'daily': timedelta(days=1),
        'every_other_day': timedelta(days=2),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(weeks=4),
    }
    interval = repeat_intervals.get(task.repeat, None)
    if interval:
        start_time = task.start_time
        for i in range(1, 30):  # Create tasks for the next 30 occurrences
            start_time += interval
            Task.objects.create(
                title=task.title,
                description=task.description,
                start_time=start_time,
                duration=task.duration,
                status=task.status,
                repeat=task.repeat,
                category=task.category,
                color=task.color,
            )

def update_task_statuses():
    now = timezone.now()
    tasks_today = Task.objects.filter(start_time__date=now.date(), status='pending')
    tasks_yesterday = Task.objects.filter(start_time__date=now.date() - timedelta(days=1), status='in_progress')

    for task in tasks_today:
        task.status = 'in_progress'
        task.save()

    for task in tasks_yesterday:
        task.status = 'rejected'
        task.save()

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    previous_tasks = Task.objects.exclude(pk=pk).order_by('-end_time')
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if not task.end_time:
                task.duration = task.category.default_duration
                task.end_time = task.start_time + timedelta(minutes=task.duration)
            else:
                task.duration = int((task.end_time - task.start_time).total_seconds() / 60)
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'todo/task_form.html', {'form': form, 'previous_tasks': previous_tasks})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        delete_future = request.POST.get('delete_future', False)
        if delete_future:
            Task.objects.filter(title=task.title, start_time__gte=task.start_time).delete()
        else:
            task.delete()
        return redirect('task_list')
    return render(request, 'todo/task_confirm_delete.html', {'task': task})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'todo/category_list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'todo/category_form.html', {'form': form})

def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'todo/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'todo/category_confirm_delete.html', {'category': category})
