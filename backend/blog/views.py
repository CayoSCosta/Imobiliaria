from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Post, Propaganda
from .forms import PostForm, PropagandaForm

# ========================
# PUBLIC VIEWS
# ========================

def public_blog_list(request):
    posts = Post.objects.filter(ativo=True).order_by('-data_criacao')
    propagandas = Propaganda.objects.filter(ativo=True)
    return render(request, 'institucional/blog.html', {
        'posts': posts,
        'propagandas': propagandas
    })

def public_post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, ativo=True)
    propagandas = Propaganda.objects.filter(ativo=True)
    return render(request, 'institucional/post_detail.html', {
        'post': post,
        'propagandas': propagandas
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
            return redirect('custom_admin_blog_list')
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
            return redirect('custom_admin_blog_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'custom_admin/blog/post_form.html', {'form': form, 'titulo': 'Editar Post'})

@staff_member_required
def custom_admin_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post removido com sucesso!')
    return redirect('custom_admin_blog_list')

@staff_member_required
def custom_admin_criar_propaganda(request):
    if request.method == 'POST':
        form = PropagandaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propaganda criada com sucesso!')
            return redirect('custom_admin_blog_list')
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
            return redirect('custom_admin_blog_list')
    else:
        form = PropagandaForm(instance=propaganda)
    return render(request, 'custom_admin/blog/propaganda_form.html', {'form': form, 'titulo': 'Editar Propaganda'})

@staff_member_required
def custom_admin_delete_propaganda(request, propaganda_id):
    propaganda = get_object_or_404(Propaganda, id=propaganda_id)
    if request.method == 'POST':
        propaganda.delete()
        messages.success(request, 'Propaganda removida com sucesso!')
    return redirect('custom_admin_blog_list')
