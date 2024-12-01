# Generated by Django 5.1.2 on 2024-10-23 22:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blockchain', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='diddocument',
            name='controller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='controlled_dids', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='diddocumentservice',
            name='did_document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='blockchain.diddocument'),
        ),
        migrations.AddField(
            model_name='didresolutionmetadata',
            name='did',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resolution_metadata', to='blockchain.diddocument'),
        ),
        migrations.AddField(
            model_name='didtransaction',
            name='did_document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='blockchain.diddocument'),
        ),
    ]