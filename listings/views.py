from django.shortcuts import render
from .models import Listing
from .models import Category
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ListingForm
from django.db.models import Q
from django.shortcuts import redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User




def listing_list(request):
    products = Listing.objects.filter(is_active=True)

    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    categories = Category.objects.all()

    return render(request, "listings/home.html", {
        "products": products,
        "q": q,
        "categories": categories,
        "selected_category": category_slug,
    })


def listing_detail(request, pk):
    product = get_object_or_404(Listing, pk= pk)
    return render(request, 'listings/listing_detail.html', {'product': product})

@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.author = request.user
            listing.save()
            return redirect('listing')
    else:
        form = ListingForm
        return render(request, 'listings/listing_create.html', {'form': form})
    
    
    
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            User.objects.create_user(
                username=username,
                password=password  
            )

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'listings/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)

                if user.password == password:
                    request.session['user_id'] = user.id
                    return redirect('listing')
                else:
                    form.add_error(None, "Неверный пароль")

            except User.DoesNotExist:
                form.add_error(None, "Пользователь не найден")
    else:
        form = LoginForm()

    return render(request, 'listings/login.html', {'form': form})


    
def logout_view(request):
    request.session.flush()
    return redirect('listing')



@login_required
def my_listings(request):
    listings = Listing.objects.filter(author=request.user)
    return render(request, 'listings/my_listings.html', {'listings': listings})


