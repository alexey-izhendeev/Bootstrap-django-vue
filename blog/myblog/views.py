from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Post
from django.core.paginator import Paginator
from .forms import SignUpForm, SignInForm, FeedBackForm
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from dotenv import load_dotenv
import os
from django.db.models import Q


# environment variables
load_dotenv()


class MainView(View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'myblog/home.html', context={
            'page_obj': page_obj
        })


class PostDetailView(View):

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, url=slug)

        return render(request, 'myblog/post_detail.html', context={
            'post': post
        })


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, 'myblog/signup.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')

        return render(request, 'myblog/signup.html', context={
            'form': form,
        })


class SignInView(View):

    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'myblog/signin.html', context={
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'myblog/signin.html', context={
            'form': form,
        })


class FeedBackView(View):

    def get(self, request, *args, **kwargs):
        form = FeedBackForm()
        return render(request, 'myblog/contact.html', context={
            'form': form,
            'title': 'Написать мне'
        })

    def post(self, request, *args, **kwargs):
        form = FeedBackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_mail(f'From {name} | {subject}', message, from_email, os.environ['EMAIL_HOST_USER'])
            except BadHeaderError:
                return HttpResponse('Невалидный заголовок')
            return HttpResponseRedirect('success')
        return render(request, 'myblog/contact.html', context={
            'form': form,
            'title': 'Написать мне'
        })


class SuccessView(View):  # User redirected here, after success FeedBack

    def get(self, request, *args, **kwargs):
        return render(request, 'myblog/success.html', context={
            'title': 'Спасибо'
        })


class SearchResultsView(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        results = ''
        if query:
            results = Post.objects.filter(
                Q(h1__icontains=query) | Q(content__icontains=query)
            )
        paginator = Paginator(results, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'myblog/search.html', context={
            'title': 'Поиск',
            'results': page_obj,
            'count': paginator.count
        })

