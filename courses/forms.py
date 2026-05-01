"""courses/forms.py"""
from django import forms


def _add_bootstrap(form):
    for field in form.fields.values():
        cls = form.fields[list(form.fields.keys())[list(form.fields.values()).index(field)]].widget.__class__.__name__
        if cls not in ("CheckboxInput","FileInput"):
            form.fields[list(form.fields.keys())[list(form.fields.values()).index(field)]].widget.attrs.setdefault("class","form-control")
    return form
from .models import Course, CourseMaterial


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget.__class__.__name__
            if w not in ('CheckboxInput', 'FileInput', 'ClearableFileInput'):
                field.widget.attrs.setdefault('class', 'form-control')
            elif w == 'FileInput' or w == 'ClearableFileInput':
                field.widget.attrs.setdefault('class', 'form-control')





class CourseForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = Course
        fields = ['title', 'description', 'category', 'thumbnail', 'level', 'status', 'max_students', 'start_date', 'end_date', 'youtube_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date':   forms.DateInput(attrs={'type': 'date'}),
        }


class CourseMaterialForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = CourseMaterial
        fields = ['title', 'material_type', 'file', 'url', 'description', 'order']

