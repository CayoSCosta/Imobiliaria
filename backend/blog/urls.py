from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('blog/', views.public_blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.public_post_detail, name='blog_post_detail'),

    # Custom Admin views
    path('custom-admin/blog/', views.custom_admin_blog_list, name='custom_admin_blog_list'),
    path('custom-admin/blog/post/novo/', views.custom_admin_criar_post, name='custom_admin_criar_post'),
    path('custom-admin/blog/post/<int:post_id>/editar/', views.custom_admin_editar_post, name='custom_admin_editar_post'),
    path('custom-admin/blog/post/<int:post_id>/delete/', views.custom_admin_delete_post, name='custom_admin_delete_post'),
    
    path('custom-admin/blog/propaganda/nova/', views.custom_admin_criar_propaganda, name='custom_admin_criar_propaganda'),
    path('custom-admin/blog/propaganda/<int:propaganda_id>/editar/', views.custom_admin_editar_propaganda, name='custom_admin_editar_propaganda'),
    path('custom-admin/blog/propaganda/<int:propaganda_id>/delete/', views.custom_admin_delete_propaganda, name='custom_admin_delete_propaganda'),
]
