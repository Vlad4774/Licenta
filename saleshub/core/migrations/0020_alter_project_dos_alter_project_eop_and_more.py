# Generated by Django 5.1.6 on 2025-03-24 19:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_alter_project_acquisition_probability'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='dos',
            field=models.DateField(null=True, verbose_name='Date of Start'),
        ),
        migrations.AlterField(
            model_name='project',
            name='eop',
            field=models.DateField(null=True, verbose_name='End of Production'),
        ),
        migrations.AlterField(
            model_name='project',
            name='responsible',
            field=models.ForeignKey(default=1, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='project',
            name='sop',
            field=models.DateField(null=True, verbose_name='Start of Production'),
        ),
    ]
