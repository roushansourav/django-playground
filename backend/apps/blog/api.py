from rest_framework import viewsets

from apps.blog.models import Comment, Post, Tag
from apps.blog.serializers import CommentSerializer, PostSerializer, TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get("post")
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset
