from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0012_precos_imovel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imovel',
            name='numero',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
