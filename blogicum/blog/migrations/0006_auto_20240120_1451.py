# Generated by Django 3.2.16 on 2024-01-20 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20240119_1011'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('created_at',)},
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(help_text='Если установить дату и время в будущем — можно делать отложенные публикации.', verbose_name='Дата и время публикации'),
        ),
    ]
