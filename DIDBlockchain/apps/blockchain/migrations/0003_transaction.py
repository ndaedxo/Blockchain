# Generated by Django 5.1.2 on 2024-10-24 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=255)),
                ('recipient', models.JSONField()),
                ('timestamp', models.FloatField()),
                ('fee', models.FloatField(default=0.0)),
                ('signature', models.BinaryField(blank=True, null=True)),
            ],
        ),
    ]
