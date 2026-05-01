"""accounts/forms.py"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, TeacherProfile
import uuid


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

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            import random
            username = f"{username}{random.randint(1000,9999)}"
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists. Please login instead.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role       = User.Role.STUDENT
        user.email      = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
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

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            import random
            username = f"{username}{random.randint(1000,9999)}"
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists. Please login instead.'
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role       = User.Role.TEACHER
        user.email      = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
            TeacherProfile.objects.filter(user=user).update(
                department=self.cleaned_data.get('department', ''),
                specialization=self.cleaned_data.get('specialization', ''),
                qualification=self.cleaned_data.get('qualification', ''),
            )
        return user


class LoginForm(AuthenticationForm):
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
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user_obj = User.objects.get(email__iexact=email)
                self.cleaned_data['username'] = user_obj.username
            except User.DoesNotExist:
                raise forms.ValidationError('No account found with this email address.')
            except User.MultipleObjectsReturned:
                raise forms.ValidationError('Multiple accounts found. Please contact support.')
        return super().clean()


class UserProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'bio', 'phone']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This email is already used by another account.')
        return email


class StudentProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = StudentProfile
        fields = ['department', 'year_of_study', 'date_of_birth']
        widgets = {'date_of_birth': forms.DateInput(attrs={'type': 'date'})}


class TeacherProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model  = TeacherProfile
        fields = ['department', 'specialization', 'qualification', 'years_experience']