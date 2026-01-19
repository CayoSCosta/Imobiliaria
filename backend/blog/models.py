from django.db import models
from django.utils.text import slugify

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    conteudo = models.TextField()
    imagem_capa = models.ImageField(upload_to='blog/capas/', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    
    class Meta:
         ordering = ['-data_criacao']

class Propaganda(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='blog/propagandas/')
    link_destino = models.URLField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
