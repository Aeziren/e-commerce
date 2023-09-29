from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment, Watchlist


def index(request):
    # Get all listings
    listings = Listing.objects.all()

    # Add to all listings a temporary atribute, highest_bid
    for listing in listings:
        highest_bid = listing.bids.order_by("value").last()
        listing.highest_bid = highest_bid

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="login")
def new_listing(request):
    if request.method == "POST":
        # Collect all data from request
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.POST.get("image")
        initial_price = request.POST.get("initial_price")
        category_title = request.POST.get("category")
        user = request.user

        # Get the category
        try:
            category = Category.objects.get(title=category_title)
        except:
            category = None

        # Create new object Listing with collected data and save it
        new_listing = Listing(title=title, description=description, image=image, initial_price=initial_price, category=category, user=user)

        new_listing.save()

        return redirect("index")

    return render(request, "auctions/new_listing.html", {
        "categories": Category.objects.all()
    })


def listings(request, id):
    # Get the current listing and its highest bid
    listing = Listing.objects.get(pk=id)
    highest_bid = listing.bids.order_by("value").last()

    if request.method == "POST":
        if "btn_bid" in request.POST:
            # Get bid inputed by user
            bid = float(request.POST.get("bid"))

            # Check if the value is valid
            if bid > listing.initial_price and (not highest_bid or bid > highest_bid.value):
                # Proceed to object creation and save
                new_bid = Bid(value=bid, listing=listing, user=request.user)
                new_bid.save()

        elif "btn_comment" in request.POST:
            # Get comment made by user
            comment = request.POST.get("comment")

            # Proceed to object creation and save
            new_comment = Comment(text=comment, listing=listing, user=request.user)
            new_comment.save()

        elif "btn_close" in request.POST:
            # Change value active to False on current listing and save
            listing.active = False
            listing.save()

        elif "watch" in request.POST:
            # Create a new Watchlist object
            watchlist_item = Watchlist(listing=listing, user=request.user)
            watchlist_item.save()

        elif "watching" in request.POST:
            # Remove a specific Watchlist object
            watchlist_item = Watchlist.objects.get(listing=listing, user=request.user)
            watchlist_item.delete()

        return redirect("listings", id)

    # This variable watching is used on the template to dynamically show the button watchlist
    try:
        Watchlist.objects.get(user=request.user, listing=listing)
        watching = True
    except:
        watching = False

    return render(request, "auctions/listings.html", {
        "listing": listing,
        "user": request.user,
        "highest_bid": highest_bid,
        "comments": listing.comments.all,
        "watching": watching
    })

@login_required(login_url="login")
def watchlist(request):
    # Get the watchlist for that specific user
    user_watchlist = Watchlist.objects.filter(user=request.user)

    # Add to each listing in the watchlist a temporary atribute, highest_bid
    for item in user_watchlist:
        listing = item.listing
        highest_bid = listing.bids.order_by("value").last()
        listing.highest_bid = highest_bid


    return render(request, "auctions/watchlist.html", {
        "user_watchlist": user_watchlist,
    })


def categories(request, title=0):
    # Check for existence of addition parameter in url
    if title:
        # This block will try to get the category and show the list of listings to the user
        # If can't find the listing (e.g: User typed in url), show the list of categories again
        try:
            chosen_category = Category.objects.get(title=title)

            listings = Listing.objects.filter(category=chosen_category)

            # Add to each listing a temporary atribute, highest_bid. Third time needed to do this on code.
            # Maybe it would be better to create a field on Listing model for the highest_bid
            for listing in listings:
                highest_bid = listing.bids.order_by("value").last()
                listing.highest_bid = highest_bid

            return render(request, "auctions/index.html", {
                "listings": listings,
                "category": chosen_category
            })

        except Category.DoesNotExist:
            pass
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })
