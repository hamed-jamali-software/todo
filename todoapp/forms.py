from django import forms
from .models import Task, Category
from django_flatpickr.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django_flatpickr.schemas import FlatpickrOptions



class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'start_time', 'end_time', 'duration',
            'status', 'repeat', 'category', 'color'
        ]
        widgets = {
            'start_time': DateTimePickerInput(
                options=FlatpickrOptions(altFormat="Y-m-d H:m",   time_24hr=True),
                attrs={"class": "start_time"},

            ),
            'end_time': DateTimePickerInput(),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'duration': forms.Select(choices=[(15, '15 minutes'), (30, '30 minutes'), (60, '1 hour'), (120, '2 hours')]),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color', 'default_duration']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'default_duration': forms.Select(choices=[(15, '15 minutes'), (30, '30 minutes'), (60, '1 hour'), (120, '2 hours')]),
        }
