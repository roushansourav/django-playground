from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.blog.models import Post


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(published=True)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"


class PostCreateView(CreateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        # Stage 2 replaces this with self.request.user once auth exists.
        form.instance.author = get_user_model().objects.first()
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"


class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
