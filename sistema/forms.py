from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import PerfilCliente, PerfilFuncionario, HorarioDisponivel, Consulta

class RegistroClienteForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    matricula = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirme a Senha',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

class RegistroFuncionarioForm(forms.ModelForm):
    especialidade = forms.CharField(
        label='Especialidade',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Usuário',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirme a Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class HorarioForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponivel
        fields = ['data', 'hora_inicio', 'hora_fim']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.funcionario = kwargs.pop('funcionario', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fim = cleaned_data.get('hora_fim')

        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise forms.ValidationError("O horário de início deve ser antes do horário de fim.")

        funcionario = self.funcionario or getattr(self.instance, 'funcionario', None)
        if funcionario and data and hora_inicio and hora_fim:
            conflitos = HorarioDisponivel.objects.filter(
                funcionario=funcionario,
                data=data,
                hora_inicio__lt=hora_fim,
                hora_fim__gt=hora_inicio
            )
            if self.instance.pk:
                conflitos = conflitos.exclude(pk=self.instance.pk)

            if conflitos.exists():
                raise forms.ValidationError("Este horário já está ocupado para este funcionário.")

        return cleaned_data

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['funcionario', 'horario', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'funcionario' in self.data:
            try:
                funcionario_id = int(self.data.get('funcionario'))
                self.fields['horario'].queryset = HorarioDisponivel.objects.filter(
                    funcionario_id=funcionario_id
                ).exclude(
                    id__in=Consulta.objects.values_list('horario_id', flat=True)
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['horario'].queryset = self.instance.funcionario.horarios_disponiveis.exclude(
                id__in=Consulta.objects.values_list('horario_id', flat=True)
            )

class EditarPerfilForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')