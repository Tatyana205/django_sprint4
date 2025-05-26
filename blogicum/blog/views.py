from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, ProfileEditForm
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.select_related(
        'category'
    ).filter(
        pub_date__date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count("comments")
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.select_related(
            'category'
        ), id=post_id
    )

    if (
        (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > timezone.now()
        )
        and request.user != post.author
    ):
        raise Http404("Пост не доступен")

    comments = Comment.objects.filter(post=post).order_by('created_at')
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
        slug=category_slug
    )
    post_list = Post.objects.select_related(
        'category'
    ).filter(
        pub_date__date__lte=timezone.now(),
        is_published=True,
        category__slug=category_slug
    ).annotate(
        comment_count=Count("comments")
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def create_post(request):
    template = 'blog/create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    template = 'blog/create.html'

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    is_owner = request.user == user
    if is_owner:
        posts = Post.objects.filter(
            author=user
        ).annotate(
            comment_count=Count("comments")
        ).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=user,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count("comments")
        ).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html', {
        'profile': user,
        'is_owner': is_owner,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserCreationForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/comment.html', {'form': form})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment
    })
