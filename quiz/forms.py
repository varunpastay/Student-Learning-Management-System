from django import forms
from .models import Quiz, Question, Choice
from django.forms import inlineformset_factory

class QuizForm(forms.ModelForm):
    class Meta:
        model  = Quiz
        fields = ['course','title','description','time_limit','pass_score','is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'time_limit': forms.NumberInput(attrs={'class':'form-control'}),
            'pass_score': forms.NumberInput(attrs={'class':'form-control'}),
            'course': forms.Select(attrs={'class':'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }
    def __init__(self,*args,teacher=None,**kwargs):
        super().__init__(*args,**kwargs)
        if teacher:
            self.fields['course'].queryset = teacher.courses_taught.filter(status='published')

class QuestionForm(forms.ModelForm):
    class Meta:
        model  = Question
        fields = ['text','marks','explanation','order']
        widgets = {
            'text': forms.Textarea(attrs={'rows':2,'class':'form-control','placeholder':'Enter question...'}),
            'marks': forms.NumberInput(attrs={'class':'form-control','min':1}),
            'explanation': forms.Textarea(attrs={'rows':2,'class':'form-control','placeholder':'Optional explanation...'}),
            'order': forms.NumberInput(attrs={'class':'form-control'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model  = Choice
        fields = ['text','is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class':'form-control','placeholder':'Choice text...'}),
            'is_correct': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }

ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=4, max_num=6, can_delete=True)
