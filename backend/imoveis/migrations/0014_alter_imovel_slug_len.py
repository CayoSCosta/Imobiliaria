from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0013_alter_imovel_numero_len'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imovel',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
