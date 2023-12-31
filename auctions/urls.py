from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listings/<int:id>", views.listings, name="listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:title>", views.categories, name="categories"),
]
