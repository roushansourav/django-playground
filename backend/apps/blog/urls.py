from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<slug:slug>/comments/new/", views.CommentCreateView.as_view(), name="comment_create"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
