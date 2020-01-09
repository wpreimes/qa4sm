# Generated by Django 2.2 on 2019-07-31 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validator', '0007_auto_20190517_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='validationrun',
            name='anomalies',
            field=models.CharField(choices=[('none', 'n/a'), ('moving_avg_35_d', '35 day moving average'), ('climatology', 'climatology')], default='none', max_length=20),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='anomalies_from',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='validationrun',
            name='anomalies_to',
            field=models.DateTimeField(null=True),
        ),
    ]
