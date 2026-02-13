from django.contrib import admin
from .models import Post, Propaganda, Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'status', 'is_featured', 'data_publicacao')
    list_filter = ('status', 'categoria', 'is_featured', 'data_publicacao')
    search_fields = ('titulo', 'conteudo')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'data_publicacao'

admin.site.register(Propaganda)
