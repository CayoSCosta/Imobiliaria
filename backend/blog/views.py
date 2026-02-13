from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Post, Propaganda, Categoria
from .forms import PostForm, PropagandaForm
from imoveis.models import Imovel
from django.db.models import Q, Prefetch, Count

# ========================
# PUBLIC VIEWS
# ========================

def public_blog_list(request):
    """
    Lista de posts públicos com busca e sidebar.
    """
    termo = request.GET.get('busca')
    categoria_slug = request.GET.get('categoria')
    
    posts = Post.objects.filter(status='publicado').select_related('categoria').only(
        'titulo', 'slug', 'imagem_capa', 'data_publicacao', 'conteudo', 'is_featured', 'categoria__nome', 'categoria__slug'
    ).order_by('-data_publicacao')

    if termo:
        posts = posts.filter(
            Q(titulo__icontains=termo) | 
            Q(conteudo__icontains=termo)
        )

    if categoria_slug:
        posts = posts.filter(categoria__slug=categoria_slug)

    # Sidebar: Posts Recentes
    recent_posts = Post.objects.filter(status='publicado').order_by('-data_publicacao')[:5]

    # Sidebar: Categorias com contagem
    categorias = Categoria.objects.annotate(total_posts=Count('posts', filter=Q(posts__status='publicado'))).filter(total_posts__gt=0)


    # Sidebar: Imóveis em Destaque
    imoveis_destaque = Imovel.objects.filter(ativo=True, destaque_blog=True).only(
        'titulo', 'bairro', 'preco', 'slug'
    ).prefetch_related('imagens')[:3]

    propagandas = Propaganda.objects.filter(ativo=True)

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'recent_posts': recent_posts,
        'imoveis_destaque': imoveis_destaque,
        'propagandas': propagandas,
        'categorias': categorias,
        'busca': termo,
        'categoria_ativa': categoria_slug
    })

def public_post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='publicado')
    
    # Contexto da Sidebar
    recent_posts = Post.objects.filter(status='publicado').exclude(id=post.id).order_by('-data_publicacao')[:5]
    categorias = Categoria.objects.annotate(total_posts=Count('posts', filter=Q(posts__status='publicado'))).filter(total_posts__gt=0)
    propagandas = Propaganda.objects.filter(ativo=True)
    
    # Posts Relacionados (mesma categoria)
    related_posts = Post.objects.filter(status='publicado', categoria=post.categoria).exclude(id=post.id).order_by('-data_publicacao')[:3]

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'recent_posts': recent_posts,
        'categorias': categorias,
        'propagandas': propagandas,
        'related_posts': related_posts
    })
    
    # Próximos posts/Relacionados (Simples)
    related_posts = Post.objects.filter(status='publicado').exclude(id=post.id).order_by('-data_publicacao')[:3]

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'propagandas': propagandas,
        'related_posts': related_posts
    })

# ========================
# CUSTOM ADMIN VIEWS
# ========================

@staff_member_required
def custom_admin_blog_list(request):
    posts = Post.objects.all()
    propagandas = Propaganda.objects.all()
    return render(request, 'custom_admin/blog/blog_list.html', {
        'posts': posts,
        'propagandas': propagandas
    })

@staff_member_required
def custom_admin_criar_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post criado com sucesso!')
            return redirect('blog:custom_admin_blog_list')
    else:
        form = PostForm()
    return render(request, 'custom_admin/blog/post_form.html', {'form': form, 'titulo': 'Novo Post'})

@staff_member_required
def custom_admin_editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post atualizado com sucesso!')
            return redirect('blog:custom_admin_blog_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'custom_admin/blog/post_form.html', {'form': form, 'titulo': 'Editar Post'})

@staff_member_required
def custom_admin_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post removido com sucesso!')
    return redirect('blog:custom_admin_blog_list')

@staff_member_required
def custom_admin_criar_propaganda(request):
    if request.method == 'POST':
        form = PropagandaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propaganda criada com sucesso!')
            return redirect('blog:custom_admin_blog_list')
    else:
        form = PropagandaForm()
    return render(request, 'custom_admin/blog/propaganda_form.html', {'form': form, 'titulo': 'Nova Propaganda'})

@staff_member_required
def custom_admin_editar_propaganda(request, propaganda_id):
    propaganda = get_object_or_404(Propaganda, id=propaganda_id)
    if request.method == 'POST':
        form = PropagandaForm(request.POST, request.FILES, instance=propaganda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propaganda atualizada com sucesso!')
            return redirect('blog:custom_admin_blog_list')
    else:
        form = PropagandaForm(instance=propaganda)
    return render(request, 'custom_admin/blog/propaganda_form.html', {'form': form, 'titulo': 'Editar Propaganda'})

@staff_member_required
def custom_admin_delete_propaganda(request, propaganda_id):
    propaganda = get_object_or_404(Propaganda, id=propaganda_id)
    if request.method == 'POST':
        propaganda.delete()
        messages.success(request, 'Propaganda removida com sucesso!')
    return redirect('blog:custom_admin_blog_list')
