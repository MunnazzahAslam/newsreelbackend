from django.urls import path


from .views import (
    FeedView,
    PSACreateView,
    PollCreateView,
    MemeCreateView,
    RepostCreateView,
    ArticleCreateView,
    PostsListView,
    PostUpVoteView,
    PostRetrieveView,
    PostDetailView,
    ChoiceVoteView,
    RelatedPostsView,
    CommentsListView,
    CommentCreateView,
    RepliesListView,
)

urlpatterns = [
    path('feed/', FeedView.as_view()),
    path('psas/', PSACreateView.as_view()),
    path('polls/', PollCreateView.as_view()),
    path('memes/', MemeCreateView.as_view()),
    path('reposts/', RepostCreateView.as_view()),
    path('articles/', ArticleCreateView.as_view()),
    path('comments/', CommentCreateView.as_view()),
    path('comments/<int:pk>/replies/', RepliesListView.as_view()),
    path('posts/<int:pk>/', PostDetailView.as_view()),
    path('posts/<str:slug>/', PostRetrieveView.as_view()),
    path('users/<int:pk>/posts/', PostsListView.as_view()),
    path('posts/<int:pk>/upvote/', PostUpVoteView.as_view()),
    path('posts/<int:pk>/related/', RelatedPostsView.as_view()),
    path('posts/<int:pk>/comments/', CommentsListView.as_view()),
    path('posts/<int:post_id>/choices/<int:pk>/', ChoiceVoteView.as_view()),
]
