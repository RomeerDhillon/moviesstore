from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('<int:id>/review/<int:review_id>/report/', views.report_review, name='movies.report_review'),
    path('top-commenter/', views.top_commenter, name='movies.top_commenter'),
    path('top-movies/', views.top_movies, name='movies.top_movies'),
    path('top-purchasers/', views.top_purchaser, name='movies.top_purchaser'),
    path('<int:id>/rate/', views.rate_movie, name='movies.rate_movie'),
    path('top-purchasers-list/', views.top_purchasers_list, name='movies.top_purchasers_list'),

]