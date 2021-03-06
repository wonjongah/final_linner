from urllib.parse import urlparse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from recipe.form import ReplyForm
from recipe.models import RecipeContent, YoutubeContent, RecipeContentAttachFile

from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from mysite.views import OwnerOnlyMixin, OwnerOnlyMixin2
import json
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from django.http import FileResponse

from user.models import Profile
from django.contrib.auth.models import User

from django.utils import timezone



class UserPostListView(ListView):
    model = RecipeContent = Profile
    template_name = 'recipe/user_posts.html'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return RecipeContent.objects.filter(Rec_conMemID=user)


    def get_username_field(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Profile.objects.filter(user=user)




class RecipeTagCloudTV(TemplateView):
    template_name = 'taggit/taggit_cloud3.html'

class RecipeTaggedObjectLV(ListView):
    # template_name = 'taggit/taggit_post_list2.html'
    # model = RecipeContent
    def get(self, request, *args, **kwargs):
        queryset1 = RecipeContent.objects.filter(Rec_conTags__name=self.kwargs.get('tag'))
        # queryset2 = YoutubeContent.objects.filter(You_conTags__name=self.kwargs.get('tag'))
        ctx = {
            'tag':queryset1,
            # 'tag':queryset2
        }
        return render(request, 'taggit/taggit_post_list2.html', ctx)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context

#
# class YoutubeTaggedObjectLV(ListView):
#     template_name = 'taggit/taggit_post_list3.html'
#     model = YoutubeContent
#
#     def get_queryset(self):
#         return YoutubeContent.objects.filter(You_conTags__name=self.kwargs.get('tag'))
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['tagname'] = self.kwargs['tag']
#         return context


class ImageView(TemplateView):
    template_name = 'recipe/tinymce/popup/photo_upload.html'

class RecipeLV(ListView):
    context_object_name = 'recipe_list'

    def get(self, request, *args, **kwargs):

        queryset = RecipeContent.objects.all()

        queryset2 = YoutubeContent.objects.all()

        paginator = Paginator(queryset, 3)

        page = request.GET.get('page1', 1)

        try:
            rooms = paginator.page(page)
        except PageNotAnInteger:
            rooms = paginator.page(1)
        except EmptyPage:
            rooms = paginator.page(paginator.num_pages)


        page = request.GET.get('page2', 1)
        paginator2 = Paginator(queryset2, 3)

        try:
            rooms2 = paginator2.page(page)
        except PageNotAnInteger:
            rooms2 = paginator2.page(1)
        except EmptyPage:
            rooms2 = paginator2.page(paginator.num_pages)

        sort = request.GET.get('sort', '')

        if sort == 'Rec_conPickCount':
            queryset = queryset.order_by('-Rec_conPickCount', '-Rec_conModify')
            paginator = Paginator(queryset, 3)
            rooms = paginator.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})
        elif sort == 'Rec_conReadcount':
            queryset = queryset.order_by('-Rec_conReadcount', '-Rec_conModify')
            paginator = Paginator(queryset, 3)
            rooms = paginator.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})
        elif sort == 'Rec_conModify':
            queryset = queryset.order_by('-Rec_conModify')
            paginator = Paginator(queryset, 3)
            rooms = paginator.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})

        elif sort == 'You_conPickCount':
            queryset2 = queryset2.order_by('-You_conPickCount', '-You_conModify')
            paginator2 = Paginator(queryset2, 3)
            rooms2 = paginator2.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})
        elif sort == 'You_conReadcount':
            queryset2 = queryset2.order_by('-You_conReadcount', '-You_conModify')
            paginator2 = Paginator(queryset2, 3)
            rooms2 = paginator2.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})
        else:
            queryset2 = queryset2.order_by('-You_conModify')
            paginator2 = Paginator(queryset2, 3)
            rooms2 = paginator2.get_page(page)
            return render(request, 'recipe/recipe_list.html', {'recipe_list': queryset, 'youtube_list' : queryset2, 'rooms' : rooms, 'rooms2' : rooms2})


class RecipeDV(DetailView):
    model = RecipeContent
    context_object_name = 'recipe'
    template_name = 'recipe/recipe_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # post = context['post']
        recipe_post = self.get_object()
        recipe_post.Rec_conReadcount += 1
        recipe_post.save()
        return context

class YoutubeDV(DetailView):
    model = YoutubeContent
    context_object_name = 'youtube'
    template_name = 'recipe/youtube_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # post = context['post']
        youtube_post = self.get_object()
        youtube_post.You_conReadcount += 1
        youtube_post.save()
        return context

class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = RecipeContent
    fields = ['Rec_conName', 'Rec_conContent', 'Rec_conTags']
    success_url = reverse_lazy('recipe:recipe_listview')
    template_name = 'recipe/recipecontent_form.html'

    def form_valid(self, form):
        form.instance.Rec_conMemID = self.request.user
        form.instance.Rec_conModify = timezone.now()
        response = super().form_valid(form)

        files = self.request.FILES.getlist('recipe_files')
        print(files)
        for file in files:
            attach_file = RecipeContentAttachFile(post=self.object, filename=file.name, size=file.size, content_type=file.content_type, upload_file=file)
            attach_file.save()
        return response


class YoutubeCreateView(LoginRequiredMixin, CreateView):
    model = YoutubeContent
    fields = ['You_conName', 'You_conContent', 'You_conTags']
    success_url = reverse_lazy('recipe:recipe_listview')
    template_name = 'recipe/youtubecontent_form.html'

    def form_valid(self, form):
        form.instance.You_conMemID = self.request.user
        return super().form_valid(form)



class RecipeUpdateView(OwnerOnlyMixin, UpdateView):

    model = RecipeContent
    fields = ['Rec_conName', 'Rec_conContent', 'Rec_conTags']
    success_url = reverse_lazy('recipe:recipe_listview')

    def form_valid(self, form):
        form.instance.Rec_conModify = timezone.now()
        response = super().form_valid(form)

        delete_files = self.request.POST.getlist("delete_files")
        for fid in delete_files:
            file = RecipeContentAttachFile.objects.get(id=int(fid))
            file_path = os.path.join(settings.MEDIA_ROOT,str(file.upload_file))
            os.remove(file_path)
            file.delete()
        # 업로드 파일 얻기
        files = self.request.FILES.getlist('recipe_files')
        for file in files:
            attach_file = RecipeContentAttachFile(post=self.object, filename=file.name, size=file.size, content_type=file.content_type, upload_file=file)
            attach_file.save()
        return response


class YoutubeUpdateView(OwnerOnlyMixin2, UpdateView):

    model = YoutubeContent
    fields = ['You_conName',  'You_conContent', 'You_conTags']
    success_url = reverse_lazy('recipe:recipe_listview')


class RecipeDeleteView(OwnerOnlyMixin, DeleteView):

    model = RecipeContent
    success_url = reverse_lazy('recipe:recipe_listview')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    # 삭제창 굳이 안 보여주게!!!!!!!!!!!!!!!!!!

class YoutubeDeleteView(OwnerOnlyMixin2, DeleteView):

    model = YoutubeContent
    success_url = reverse_lazy('recipe:recipe_listview')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@login_required
@require_POST
def recipe_like(request):
    pk = request.POST.get('pk', None)
    recipe = get_object_or_404(RecipeContent, pk=pk)
    user = request.user

    if recipe.Rec_conLikesUser.filter(id=user.id).exists():
        recipe.Rec_conLikesUser.remove(user)
        if recipe.Rec_conPickCount == 0:
            recipe.Rec_conPickCount = 0
        else:
            recipe.Rec_conPickCount -= 1
        recipe.save()
        message = '좋아요 취소'
    else:
        recipe.Rec_conLikesUser.add(user)
        recipe.Rec_conPickCount += 1
        recipe.save()
        message = '좋아요'

    context = {'rec_likes_count':recipe.rec_count_likes_user(), 'message': message}
    return HttpResponse(json.dumps(context), content_type="application/json")

class recipe_like_list(ListView):
    template_name = 'recipe/recipe_list_like.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, '로그인을 먼저 하세요')
            return HttpResponseRedirect('/')
        return super().dispatch( request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        user = self.request.user
        queryset = user.Rec_conLikesUser.all()
        queryset2 = user.You_conLikesUser.all()
        paginator = Paginator(queryset, 3)

        page = request.GET.get('page1', 1)

        try:
            rooms = paginator.page(page)
        except PageNotAnInteger:
            rooms = paginator.page(1)
        except EmptyPage:
            rooms = paginator.page(paginator.num_pages)


        page = request.GET.get('page2', 1)
        paginator2 = Paginator(queryset2, 3)

        try:
            rooms2 = paginator2.page(page)
        except PageNotAnInteger:
            rooms2 = paginator2.page(1)
        except EmptyPage:
            rooms2 = paginator2.page(paginator.num_pages)

        ctx = {'recipe': queryset,
               'youtube_list' : queryset2,
               'rooms' : rooms,
               'rooms2' : rooms2}
        return render(request, 'recipe/recipe_list_like.html', ctx)


@login_required
@require_POST
def youtube_like(request):
    pk = request.POST.get('pk', None)
    youtube = get_object_or_404(YoutubeContent, pk=pk)
    user = request.user

    if youtube.You_conLikesUser.filter(id=user.id).exists():
        youtube.You_conLikesUser.remove(user)
        message = '좋아요 취소'
    else:
        youtube.You_conLikesUser.add(user)
        message = '좋아요'

    context = {'you_likes_count':youtube.you_count_likes_user(), 'message': message}
    return HttpResponse(json.dumps(context), content_type="application/json")



def recipe_download(request, id):
    file= RecipeContentAttachFile.objects.get(id=id)
    file_path = os.path.join(settings.MEDIA_ROOT,str(file.upload_file))

    return FileResponse(open(file_path,'rb'))

# def RecipeDV(request, Rec_conId):
#     recipe = get_object_or_404(RecipeContent, pk=Rec_conId)
#
#     if request.method == "POST":
#         reply_form = ReplyForm(request.POST)
#         reply_form.instance.Rep_name_id = request.user.id
#         reply_form.instance.Rep_conid_id = Rep_conid