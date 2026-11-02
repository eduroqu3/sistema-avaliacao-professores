import uuid
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('avaliacoes', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='evaluation', name='public_id', field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
        migrations.AddField(model_name='evaluation', name='updated_at', field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now), preserve_default=False),
        migrations.CreateModel(name='StudentProfile', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('display_name', models.CharField(max_length=120, verbose_name='Nome de exibição')), ('active', models.BooleanField(default=True, verbose_name='Conta ativa')), ('created_at', models.DateTimeField(auto_now_add=True)), ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL))], options={'verbose_name': 'Conta de aluno', 'verbose_name_plural': 'Contas de alunos', 'ordering': ['display_name']}),
        migrations.CreateModel(name='StudentEvaluationRecord', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('encrypted_evaluation_id', models.TextField(verbose_name='Recibo de resposta criptografado')), ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='participation_records', to='avaliacoes.teachingassignment')), ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_records', to=settings.AUTH_USER_MODEL))], options={'verbose_name': 'Controle de participação do aluno', 'verbose_name_plural': 'Controles de participação dos alunos'}),
        migrations.AddConstraint(model_name='studentevaluationrecord', constraint=models.UniqueConstraint(fields=('student', 'assignment'), name='one_student_evaluation_per_assignment')),
    ]
