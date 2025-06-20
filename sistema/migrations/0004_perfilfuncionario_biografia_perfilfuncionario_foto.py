# Generated by Django 5.1.7 on 2025-06-10 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0003_remove_perfilcliente_foto_perfil_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilfuncionario',
            name='biografia',
            field=models.TextField(blank=True, help_text='Um breve resumo sobre sua experiência e abordagem.', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='perfilfuncionario',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='fotos_perfil/'),
        ),
    ]
