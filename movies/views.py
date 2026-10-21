from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required, user_passes_test
from cart.models import Item
from django.db.models import Avg


def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported = False)
    # every rating that has been given for this movie
    ratings = Rating.objects.filter(movie=movie)
    # average the stars column
    average_rating = ratings.aggregate(Avg('stars'))['stars__avg']
    #find users rating
    user_rating = None
    if request.user.is_authenticated: 
        user_rating = ratings.filter(user=request.user).first()
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['average_rating'] = average_rating
    template_data['rating_count'] = ratings.count()
    template_data['user_rating'] = user_rating
    template_data['star_options'] = [1, 2, 3, 4, 5]
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)


@login_required
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    #only accept a post request with a value of 1-5
    if request.method == 'POST' and request.POST.get('stars') in ['1', '2', '3', '4', '5']: 
        Rating.objects.update_or_create(
            movie=movie, 
            user=request.user,
            defaults={'stars': int(request.POST['stars'])}
        )
    return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        review.reported = True
        review.save()
        review.delete()
    return redirect('movies.show', id=id)

@user_passes_test(lambda u: u.is_superuser)
def top_commenter(request):
    # go through every comment 
    # userid : number 
    #keep a running int of largest comment, keep user id correlated to that 

    counts = {}
    max = 0
    max_user = None

    for review in Review.objects.all():
        if review.user.id not in counts: 
            counts[review.user.id] = 0

        counts[review.user.id] += 1
        if (counts[review.user.id] > max):
            max = counts[review.user.id]
            max_user = review.user.username

    #page name 
    template_data = {}
    template_data['title'] = 'Top Commenter'

    template_data['top_user'] = max_user
    template_data['count'] = max

    return render(request, 'movies/top_commenter.html',
        {'template_data': template_data})

@user_passes_test(lambda u: u.is_superuser)
def top_movies(request):
    review_counts = {}
    most_reviewed = None
    most_reviewed_count = 0
    for review in Review.objects.all():
        if review.movie.id not in review_counts:
            review_counts[review.movie.id] = 0
        review_counts[review.movie.id] += 1
        if review_counts[review.movie.id] > most_reviewed_count:
            most_reviewed_count = review_counts[review.movie.id]
            most_reviewed = review.movie.name

    purchase_counts = {}
    most_bought = None
    most_bought_count = 0
    for item in Item.objects.all():
        if item.movie.id not in purchase_counts:
            purchase_counts[item.movie.id] = 0
        purchase_counts[item.movie.id] += item.quantity
        if purchase_counts[item.movie.id] > most_bought_count:
            most_bought_count = purchase_counts[item.movie.id]
            most_bought = item.movie.name
    template_data = {}
    template_data['title'] = 'Top Movies'
    template_data['most_reviewed'] = most_reviewed
    template_data['most_reviewed_count'] = most_reviewed_count
    template_data['most_bought'] = most_bought
    template_data['most_bought_count'] = most_bought_count
    return render(
        request,
        'movies/top_movies.html',
        {'template_data': template_data}
    )