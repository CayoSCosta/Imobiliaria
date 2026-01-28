from django.db import migrations, models


def move_preco_to_imovel(apps, schema_editor):
    Imovel = apps.get_model('imoveis', 'Imovel')
    Unidade = apps.get_model('imoveis', 'Unidade')

    for imovel in Imovel.objects.all():
        min_preco = (
            Unidade.objects.filter(imovel_id=imovel.id)
            .exclude(preco__isnull=True)
            .order_by('preco')
            .values_list('preco', flat=True)
            .first()
        )
        if min_preco is not None and imovel.preco is None:
            imovel.preco = min_preco
            imovel.save(update_fields=['preco'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('imoveis', '0011_imovel_destaque'),
    ]

    operations = [
        migrations.AddField(
            model_name='imovel',
            name='preco',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço'),
        ),
        migrations.AddField(
            model_name='imovel',
            name='preco_m2',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Preço do m²'),
        ),
        migrations.AddField(
            model_name='imovel',
            name='condominio',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Condomínio'),
        ),
        migrations.AddField(
            model_name='imovel',
            name='iptu',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='IPTU'),
        ),
        migrations.AddField(
            model_name='imovel',
            name='parcela',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Parcela'),
        ),
        migrations.RunPython(move_preco_to_imovel, noop),
        migrations.RemoveField(
            model_name='unidade',
            name='preco',
        ),
    ]
