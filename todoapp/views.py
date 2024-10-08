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
            'start': task.start_time.strftime('%Y-%m-%d %H:%M'),
            'end': task.end_time.strftime('%Y-%m-%d %H:%M'),
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
        update_task_statuses()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def task_list(request):
    today = timezone.now().date()
    day_filter = request.GET.get('day')

    # Task.objects.filter(start_time__date=now.date()).order_by('-end_time')
    not_filter = False
    if day_filter == 'yesterday':
        start_date = today - timedelta(days=1)
    elif day_filter == 'tomorrow':
        start_date = today + timedelta(days=1)
    elif day_filter == 'today':
        start_date = today
    else:
        not_filter = True

    if not_filter:
        tasks = Task.objects.all().order_by('start_time')
    else:
        tasks = Task.objects.filter(start_time__date=start_date).order_by('start_time')

    return render(request, 'todo/task_list.html', {'tasks': tasks, 'current_day': day_filter})

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
        'aweek': timedelta(days=1),
        '3days': timedelta(days=1),
        '2days': timedelta(days=1),
        'amonth': timedelta(days=1),
        'once-aweek': timedelta(weeks=1),
    }
    interval = repeat_intervals.get(task.repeat, None)
    if interval:
        start_time = task.start_time
        repeat_days = 0
        if task.repeat == 'aweek':
            repeat_days = 7
        elif task.repeat == '3days':
            repeat_days = 3
        elif task.repeat == '2days':
            repeat_days = 2
        elif task.repeat == 'amonth':
            repeat_days = 30
        elif task.repeat == 'once-aweek':
            repeat_days = 4

        for i in range(1, repeat_days):  # Create tasks for the next 30 occurrences
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
