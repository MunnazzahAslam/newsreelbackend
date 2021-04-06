from rest_framework.response import Response
from rest_framework import filters, status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS

from drf_yasg.utils import swagger_auto_schema

from reviews.models import Review
from .serializers import ReviewDetailSerializer, VoteSerializer, ReplySerializer


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = ReviewDetailSerializer


class ReviewsView(generics.ListCreateAPIView):
    serializer_class = ReviewDetailSerializer
    ordering_fields = ('id', 'rating')
    filter_backends = [filters.OrderingFilter]

    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        if not user_id or not user_id.isdigit():
            raise ValidationError({'user_id': 'Invalid user_id'})

        return Review.objects.filter(user_id=user_id).order_by('id')

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [permission() for permission in (AllowAny, )]
        else:
            return [permission() for permission in (IsAuthenticated, )]


class ReviewVoteView(generics.GenericAPIView):
    queryset = Review.objects.all()

    @swagger_auto_schema(operation_description="Vote Review", request_body=VoteSerializer(),
                         responses={200: ReviewDetailSerializer()})
    def post(self, request, pk):
        review = self.get_object()
        serializer = VoteSerializer(review, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        review_serializer = ReviewDetailSerializer(review, context={'request': request})
        return Response(review_serializer.data, status=status.HTTP_200_OK)


class ReplyVoteView(generics.GenericAPIView):
    queryset = Review.objects.all()

    @swagger_auto_schema(operation_description="Vote Reply", request_body=VoteSerializer(),
                         responses={200: ReviewDetailSerializer()})
    def post(self, request, pk):
        review = self.get_object()
        serializer = VoteSerializer(review.reply, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        review_serializer = ReviewDetailSerializer(review, context={'request': request})
        return Response(review_serializer.data, status=status.HTTP_200_OK)


class RepliesView(generics.GenericAPIView):
    queryset = Review.objects.all()

    @swagger_auto_schema(operation_description="Reply", request_body=ReplySerializer(),
                         responses={200: ReviewDetailSerializer()})
    def post(self, request, pk):
        review = self.get_object()
        if request.user != review.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if hasattr(review, 'reply'):
            return Response('You have already replied', status=status.HTTP_400_BAD_REQUEST)

        serializer = ReplySerializer(data={'review': review.id, **request.data}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_review = self.get_object()
        review_serializer = ReviewDetailSerializer(updated_review, context={'request': request})
        return Response(review_serializer.data, status=status.HTTP_200_OK)
