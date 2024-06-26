from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from .forms import TaskForm
from .models import Task
import datetime

from .utils import SortByPriority, SortByTag
from ..user.models import User


def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            tag_id = request.POST.get('tags')
            task.tag_id = tag_id
            priority_id = request.POST.get('priority')
            task.priority_id = priority_id
            task.created_at = datetime.datetime.now()
            task.save()
            return redirect('tasks')
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})


def tasks(request):
    if request.user.is_authenticated:
        user_tasks = Task.objects.filter(completed=False, user=request.user)
        custom_filter_priority = SortByPriority(request.GET, queryset=user_tasks)
        user_tasks = custom_filter_priority.qs
        custom_filter_tag = SortByTag(request.GET, queryset=user_tasks)
        user_tasks = custom_filter_tag.qs
        context = {'tasks': user_tasks,
                   'custom_filter_priority': custom_filter_priority,
                   'custom_filter_tag': custom_filter_tag}
        return render(request, 'tasks/my_tasks.html', context)


class HomeView(ListView):
    model = Task
    template_name = 'home.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            all_tasks = Task.objects.filter(completed=False, user=self.request.user)
            last_3_tasks = all_tasks.order_by('-created_at')[:3]
            context['last_3_tasks'] = last_3_tasks
        return context


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/edit_task.html'
    success_url = reverse_lazy('tasks')
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return self.request.user == task.user or self.request.user.is_staff

    def form_valid(self, form):
        task = form.save(commit=False)
        tag_id = self.request.POST.get('tags')
        #task.tag_id = tag_id
        task.save()
        return super().form_valid(form)


def mark_as_completed(request, task_id):
    current_page = request.META.get('HTTP_REFERER')
    task = get_object_or_404(Task, pk=task_id)
    task.completed = True
    task.save()
    return redirect(current_page)


def restore_task(request, task_id):
    current_page = request.META.get('HTTP_REFERER')
    task = get_object_or_404(Task, pk=task_id)
    task.completed = False
    task.save()
    return redirect(current_page)


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return redirect('completed tasks')


class CompletedTaskView(ListView):
    model = Task
    template_name = 'tasks/completed_tasks.html'
    context_object_name = 'completed_tasks'

    def get_queryset(self):
        return Task.objects.filter(completed=True, user=self.request.user)


def user_b_tasks(request, user_id):
    user_b_current_tasks = Task.objects.filter(user_id=user_id, visibility='PU')
    user_b = User.objects.get(pk=user_id)

    custom_filter_priority = SortByPriority(request.GET, queryset=user_b_current_tasks)
    user_b_current_tasks = custom_filter_priority.qs
    custom_filter_tag = SortByTag(request.GET, queryset=user_b_current_tasks)
    user_b_current_tasks = custom_filter_tag.qs

    context = {'user_b': user_b,
               'user_tasks': user_b_current_tasks,
               'tasks': user_b_current_tasks,
               'custom_filter_priority': custom_filter_priority,
               'custom_filter_tag': custom_filter_tag}

    return render(request, 'tasks/user_tasks.html', context)
