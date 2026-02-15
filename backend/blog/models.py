from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Post(models.Model):
    STATUS_CHOICES = (
        ('rascunho', 'Rascunho'),
        ('publicado', 'Publicado'),
    )

    titulo = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Gerado automaticamente a partir do título")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', verbose_name="Categoria")
    conteudo = models.TextField(verbose_name="Conteúdo", help_text="Use Markdown para formatar o texto")
    imagem_capa = models.ImageField(upload_to='blog/capas/', blank=True, null=True, verbose_name="Imagem de Capa")
    
    # Datas e Status
    data_publicacao = models.DateTimeField(default=timezone.now, verbose_name="Data de Publicação")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    
    # Destaque
    is_featured = models.BooleanField(default=False, verbose_name="Destaque na Home", help_text="Define se o post aparece em destaque na home do blog")

    # SEO
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name="Meta Title (SEO)", help_text="Título otimizado para buscadores (max 70 caracteres)")
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name="Meta Description (SEO)", help_text="Descrição otimizada para buscadores (max 160 caracteres)")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.titulo)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists(): # Ensure uniqueness excluding self
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo
    
    class Meta:
         ordering = ['-data_publicacao']
         verbose_name = "Post"
         verbose_name_plural = "Posts"

class Propaganda(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='blog/propagandas/')
    link_destino = models.URLField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
