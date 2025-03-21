# Generated by Django 5.1.6 on 2025-03-18 10:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionUpdates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('done_time', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'SystemActionUpdate',
                'verbose_name_plural': 'SystemActionUpdates',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arabic_name', models.CharField(max_length=50)),
                ('latin_name', models.CharField(max_length=50)),
                ('abreviated_name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'department',
                'verbose_name_plural': 'departments',
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arabic_name', models.CharField(max_length=50)),
                ('latin_name', models.CharField(max_length=50)),
                ('abreviated_name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'faculty',
                'verbose_name_plural': 'faculties',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_number', models.CharField(blank=True, max_length=200, null=True)),
                ('manufacturer', models.CharField(blank=True, max_length=200, null=True)),
                ('measurement_range', models.CharField(blank=True, max_length=200, null=True)),
                ('precision', models.CharField(blank=True, max_length=200, null=True)),
                ('power_requirements', models.CharField(blank=True, max_length=200, null=True)),
                ('dimensions', models.CharField(blank=True, max_length=200, null=True)),
                ('weight', models.CharField(blank=True, max_length=200, null=True)),
                ('published', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('available', 'Available'), ('in_use', 'In Use')], default='available', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'plan',
                'verbose_name_plural': 'plans',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField()),
                ('progress', models.IntegerField(default=0)),
                ('start_date', models.DateField()),
                ('deadline', models.DateField()),
                ('logo', models.ImageField(blank=True, null=True, upload_to='project_logos/')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('labeled', 'Labeled')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Province',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.IntegerField(default=0, help_text='Province code', unique=True, verbose_name='Province code')),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arabic_name', models.CharField(max_length=50)),
                ('latin_name', models.CharField(max_length=50)),
                ('abreviated_name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'speciality',
                'verbose_name_plural': 'specialities',
            },
        ),
        migrations.CreateModel(
            name='MaterialFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='material_files/%Y/%m/%d')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='dashboard.material')),
            ],
        ),
        migrations.CreateModel(
            name='MaterialImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='material_images/%Y/%m/%d')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='dashboard.material')),
            ],
        ),
        migrations.CreateModel(
            name='Phase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('deadline', models.DateField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phases', to='dashboard.plan')),
            ],
            options={
                'verbose_name': 'phase',
                'verbose_name_plural': 'phases',
            },
        ),
        migrations.AddField(
            model_name='plan',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plans', to='dashboard.project'),
        ),
        migrations.CreateModel(
            name='MaterialRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acquired_date', models.DateField(auto_now_add=True)),
                ('quantity', models.IntegerField(default=1)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.material')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='project_files/%Y/%m/%d')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='dashboard.project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='project_images/%Y/%m/%d')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='dashboard.project')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='dashboard.phase')),
            ],
            options={
                'verbose_name': 'task',
                'verbose_name_plural': 'tasks',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('description', models.TextField()),
                ('task', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='dashboard.task')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_permitted_to_demand', models.BooleanField(default=False)),
                ('is_project_leader', models.BooleanField(default=False)),
                ('photo', models.ImageField(upload_to='profiles_images/%Y/%m/%d')),
                ('phone', models.CharField(max_length=20)),
                ('bio', models.TextField(blank=True)),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('role', models.CharField(choices=[('supervisor', 'Supervisor'), ('member', 'Member')], max_length=20)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=20)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.department')),
                ('faculty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.faculty')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.project')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.province')),
                ('speciality', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.speciality')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='team_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
