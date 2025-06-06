from django.db import models
from django.contrib.auth.models import User

class PerfilCliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.usuario.username

class PerfilFuncionario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidade = models.CharField(max_length=100)

    def __str__(self):
        return self.usuario.username

class HorarioDisponivel(models.Model):
    funcionario = models.ForeignKey(PerfilFuncionario, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f'{self.data} - {self.hora_inicio} até {self.hora_fim}'

class Consulta(models.Model):
    cliente = models.ForeignKey(PerfilCliente, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(PerfilFuncionario, on_delete=models.CASCADE)
    horario = models.ForeignKey(HorarioDisponivel, on_delete=models.CASCADE)
    observacoes = models.TextField(blank=True)


    

    def __str__(self):
        return f'{self.cliente} com {self.funcionario} em {self.horario.data}'
    
    
