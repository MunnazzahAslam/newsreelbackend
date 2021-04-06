from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework import generics, status, mixins

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body

from .filters import PostFilter
from .permissions import IsPostOwner
from posts.models import Post, Choice, Comment
from .serializers import (
    PSASerializer,
    PostSerializer,
    PollSerializer,
    MemeSerializer,
    RepostSerializer,
    CommentSerializer,
    ArticleSerializer,
    PostUpVoteSerializer,
    ChoiceVoteSerializer,
    RelatedPostSerializer,
)

User = get_user_model()

type_param = openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING)


class CreateAPIView(generics.CreateAPIView):

    @swagger_auto_schema(tags=['posts'])
    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)


class PSACreateView(CreateAPIView):
    serializer_class = PSASerializer


class PollCreateView(CreateAPIView):
    serializer_class = PollSerializer


class MemeCreateView(CreateAPIView):
    serializer_class = MemeSerializer


class RepostCreateView(CreateAPIView):
    serializer_class = RepostSerializer


class ArticleCreateView(CreateAPIView):
    serializer_class = ArticleSerializer


class PostsListView(generics.ListAPIView):
    serializer_class = PostSerializer
    filterset_class = PostFilter
    permission_classes = (AllowAny, )

    def get_queryset(self):
        author_id = self.request.resolver_match.kwargs['pk']
        get_object_or_404(User, id=author_id)
        queryset = Post.objects.filter(author_id=author_id).order_by('-id')
        return queryset

    @swagger_auto_schema(tags=['posts'], manual_parameters=[type_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)


class PostUpVoteView(generics.GenericAPIView):
    queryset = Post.objects.all()

    @swagger_auto_schema(operation_description="Upvote Post", request_body=no_body, responses={200: PostSerializer()})
    def post(self, request, pk):
        post = self.get_object()
        serializer = PostUpVoteSerializer(post, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        review_serializer = PostSerializer(post, context={'request': request})
        return Response(review_serializer.data, status=status.HTTP_200_OK)


class ChoiceVoteView(generics.GenericAPIView):

    def get_queryset(self):
        queryset = Choice.objects.select_related('poll').select_related('poll__post').all()
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs['pk']
        post_id = self.kwargs['post_id']
        obj = get_object_or_404(queryset, pk=pk, poll__post_id=post_id)
        self.check_object_permissions(self.request, obj)

        return obj

    @swagger_auto_schema(operation_description="Vote Choice", request_body=no_body, responses={200: PostSerializer()})
    def post(self, request, post_id, pk):
        choice = self.get_object()
        serializer = ChoiceVoteSerializer(choice, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        post_serializer = PostSerializer(choice.poll.post, context={'request': request})
        return Response(post_serializer.data, status=status.HTTP_200_OK)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsPostOwner, )
    parser_classes = (MultiPartParser, )


class PostRetrieveView(generics.RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AllowAny, )


class FeedView(generics.ListAPIView):
    filterset_fields = ('category', )
    serializer_class = PostSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-upvotes', '-created_at')
        return queryset


class RelatedPostsView(generics.ListAPIView):
    pagination_class = None
    permission_classes = (AllowAny, )
    serializer_class = RelatedPostSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=pk)
        queryset = Post.objects.filter(type='article', author_id=post.author.id).exclude(pk=pk)[:3]
        return queryset


class CommentsListView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        return Comment.objects.filter(post_id=post_id, parent_comment__isnull=True).order_by('id')

    @swagger_auto_schema(tags=['comments'])
    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer


class RepliesListView(generics.ListAPIView):
    permission_classes = (AllowAny, )
    serializer_class = CommentSerializer

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_id)
        return Comment.objects.filter(parent_comment_id=comment_id).order_by('id')

    @swagger_auto_schema(tags=['comments'])
    def get(self, request, *args, **kwargs):
        return super().get(request, args, kwargs)
