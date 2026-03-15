from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, View
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Listing, Category
from .forms import ListingForm, RegisterForm, LoginForm



class HomeView(ListView):
    model = Listing
    template_name = 'listings/home.html'
    context_object_name = 'products'

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("category", "").strip()

        products = Listing.objects.filter(is_active=True)

        if q:
            products = products.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )

        if category_slug:
            products = products.filter(category__slug=category_slug)

        return products



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = cache.get("categories")

        if not categories:
            categories = list(Category.objects.all())
            cache.set("categories", categories, 600)

        context['categories'] = categories
        context['q'] = self.request.GET.get("q", "").strip()
        context['selected_category'] = self.request.GET.get("category", "").strip()

        return context


class ListingDetailView(DetailView):
    model = Listing
    template_name = 'listings/listing_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'


class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    form_class = ListingForm
    template_name = 'listings/listing_create.html'
    success_url = reverse_lazy('listing')

    def form_valid(self, form):
        form.instance.author = self.request.user
        cache.clear()
        return super().form_valid(form)


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'listings/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User.objects.create_user(username=username, password=password)
            return redirect('login')

        return render(request, 'listings/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'listings/login.html', {'form': form})

    def post(self, request):
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

        return render(request, 'listings/login.html', {'form': form})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        request.session.flush()
        return redirect('listing')


class MyListingsView(LoginRequiredMixin, ListView):
    model = Listing
    template_name = 'listings/my_listings.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return Listing.objects.filter(author=self.request.user)


class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = 'listings/favorite_listings.html'
    context_object_name = 'favorite_listings'

    def get_queryset(self):
        return self.request.user.favorite_listings.all()


class ToggleFavoriteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        user = request.user

        if user in listing.favorites.all():
            listing.favorites.remove(user)
        else:
            listing.favorites.add(user)

        return redirect('listing_detail', pk=pk)