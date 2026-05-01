"""assignments/forms.py"""
from django import forms
from .models import Assignment, Submission


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget.__class__.__name__
            if w not in ('CheckboxInput',):
                field.widget.attrs.setdefault('class', 'form-control')





class AssignmentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = Assignment
        fields = ['course', 'title', 'description', 'deadline', 'total_marks',
                  'allow_late', 'late_penalty', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.courses_taught.filter(status='published')


class SubmissionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['file', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional notes for your teacher...'}),
        }


class GradeSubmissionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ['marks_obtained', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide constructive feedback...'}),
            'marks_obtained': forms.NumberInput(attrs={'step': '0.5', 'min': '0'}),
        }

