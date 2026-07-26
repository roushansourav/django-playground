from rest_framework import serializers

from apps.blog.models import Comment, Post, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "body", "created_at"]
        read_only_fields = ["created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    tags = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "body",
            "author",
            "published",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
