from django.urls import path


from .views import ReviewsView, ReviewDetailView, ReviewVoteView, RepliesView, ReplyVoteView

urlpatterns = [
    path('reviews/', ReviewsView.as_view()),
    path('reviews/<int:pk>/', ReviewDetailView.as_view()),
    path('reviews/<int:pk>/replies/', RepliesView.as_view()),
    path('reviews/<int:pk>/replies/vote/', ReplyVoteView.as_view()),
    path('reviews/<int:pk>/vote/', ReviewVoteView.as_view()),
]
