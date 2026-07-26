from rest_framework.routers import DefaultRouter

from apps.blog.api import CommentViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")
router.register("tags", TagViewSet, basename="tag")

urlpatterns = router.urls
