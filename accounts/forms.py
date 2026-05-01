"""accounts/forms.py"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, TeacherProfile


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget.__class__.__name__
            if w not in ('CheckboxInput',):
                field.widget.attrs.setdefault('class', 'form-control')


class StudentRegistrationForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    email      = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role  = User.Role.STUDENT
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.filter(user=user).update(
                department=self.cleaned_data.get('department', '')
            )
        return user


class TeacherRegistrationForm(BootstrapMixin, UserCreationForm):
    first_name     = forms.CharField(max_length=50, required=True)
    last_name      = forms.CharField(max_length=50, required=True)
    email          = forms.EmailField(required=True)
    department     = forms.CharField(max_length=100, required=False)
    specialization = forms.CharField(max_length=200, required=False)
    qualification  = forms.CharField(max_length=200, required=False)

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role  = User.Role.TEACHER
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            TeacherProfile.objects.filter(user=user).update(
                department=self.cleaned_data.get('department', ''),
                specialization=self.cleaned_data.get('specialization', ''),
                qualification=self.cleaned_data.get('qualification', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    """Login using email instead of username."""
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        email = self.cleaned_data.get('username')  # field is named username by Django
        password = self.cleaned_data.get('password')
        if email and password:
            # Look up user by email first
            from accounts.models import User as UserModel
            try:
                user_obj = UserModel.objects.get(email__iexact=email)
                self.cleaned_data['username'] = user_obj.username
            except UserModel.DoesNotExist:
                raise forms.ValidationError('No account found with this email address.')
            except UserModel.MultipleObjectsReturned:
                raise forms.ValidationError('Multiple accounts found. Please contact support.')
        return super().clean()


class UserProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'bio', 'phone']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}


class StudentProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = StudentProfile
        fields = ['department', 'year_of_study', 'date_of_birth']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class TeacherProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = TeacherProfile
        fields = ['department', 'specialization', 'qualification', 'years_experience']
