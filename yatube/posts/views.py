from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect

from .forms import PostForm
from .models import Group, Post, User
from .utils import external_paginator


def index(request):
    post_list = Post.objects.select_related('group', 'author')

    context = {
        'page_obj': external_paginator(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()

    context = {
        'author': author,
        'page_obj': external_paginator(request, post_list),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_info = get_object_or_404(Post, pk=post_id)

    context = {
        'post_info': post_info,
        'post_id': post_id
    }
    return render(request, 'posts/post_detail.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()

    context = {
        'group': group,
        'page_obj': external_paginator(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


@login_required
@csrf_protect
def post_create(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', user.username)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        form = PostForm(request.POST or None, instance=post)
        context = {
            'form': form,
            'is_edit': True,
        }
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:post_detail', post_id)
