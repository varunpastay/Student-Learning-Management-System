from django import forms
from .models import TeacherFeedback

class FeedbackForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'star-radio'})
    )
    class Meta:
        model  = TeacherFeedback
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Share your experience with this teacher...'})}
