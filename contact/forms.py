from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from . import models

class ContactForm(forms.ModelForm):
    picture = forms.ImageField(
        label='Foto',
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*',
            }
        ),
        required=False
    )
    class Meta:
        model = models.Contact
        fields = (
            'first_name', 'last_name', 'phone',
            'email', 'description', 'category',
            'picture',
        )
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'phone': 'Telefone',
            'email': 'E-mail',
            'description': 'Observações',
            'category': 'Categoria',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        categories = models.Category.objects.none()
        if user is not None and user.is_authenticated:
            categories = models.Category.objects.filter(owner=user)
        self.fields['category'].queryset = categories.order_by('name')
        self.fields['category'].empty_label = None

    def clean_category(self):
        category = self.cleaned_data.get('category')
        owner_id = getattr(self.user, 'pk', None)
        if category and category.owner_id != owner_id:
            raise ValidationError(
                'Selecione uma categoria pertencente à sua conta.',
                code='invalid',
            )
        return category
        
    def clean(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if first_name == last_name:
            msg = ValidationError(
                'Primeiro nome não pode ser igual ao segundo',
                code='invalid'
            )
        
            self.add_error('first_name', msg)
            self.add_error('last_name', msg)

        return super().clean()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(
        label='Senha',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', required=True, min_length=3)
    last_name = forms.CharField(label='Sobrenome', required=True, min_length=3)
    email = forms.EmailField(label='E-mail')
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username', 'password1', 'password2',
        )
        labels = {'username': 'Usuário'}
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError('Já existe este e-mail', code='invalid')
            )
        return email
    
class RegisterUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        min_length=2,
        max_length=30,
        required=True,
        error_messages={
            'min_length': 'Informe pelo menos 2 letras.'
        }
    )
    last_name = forms.CharField(
        label='Sobrenome',
        min_length=2,
        max_length=30,
        required=True,
    )

    password1 = forms.CharField(
        label='Nova senha',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )

    password2 = forms.CharField(
        label='Confirme a nova senha',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='Repita a nova senha.',
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'username',
        )
        labels = {
            'email': 'E-mail',
            'username': 'Usuário',
        }

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = super().save(commit=False)
        password = cleaned_data.get('password1')

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                self.add_error(
                    'password2',
                    ValidationError('Senhas não batem')
                )

        return super().clean()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_email = self.instance.email

        if current_email != email:
            if User.objects.filter(email=email).exists():
                self.add_error(
                    'email',
                    ValidationError('Já existe este e-mail', code='invalid')
                )

        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as errors:
                self.add_error(
                    'password1',
                    ValidationError(errors)
                )

        return password1
