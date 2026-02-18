from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0021_imovel_destaque_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='imovel',
            name='ordem_exibicao',
            field=models.PositiveIntegerField(default=0, help_text='Menores números aparecem primeiro na listagem pública', verbose_name='Ordem de Exibição'),
        ),
    ]
