from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, View
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Listing, Category
from .forms import ListingForm, RegisterForm, LoginForm
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CategorySerializer
from django.forms.models import model_to_dict
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetriveDestroyAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import ListingSerializer
from rest_framework import status
from .models import Listing



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


# class ToggleFavoriteView(LoginRequiredMixin, View):
#     def get(self, request, pk):
#         listing = get_object_or_404(Listing, pk=pk)
#         user = request.user
#
#         if user in listing.favorites.all():
#             listing.favorites.remove(user)
#         else:
#             listing.favorites.add(user)
#
#         return redirect('listing_detail', pk=pk)
#
# class CategoryListApiView(APIView):
#     def get(self, request):
#         categories = Category.objects.all()
#         serializer = CategorySerializer(categories, many=True)
#         return Response(serializer.data)
#     def post(self, request):
#         post_category = Category.objects.create(
#             name=request.data['name'],
#             slug=request.data['slug']
#         )
#         return Response(
#             {
#                 'post': model_to_dict(post_category)
#             }
#         )


# показывает список всех категорий
class CategoryListApiView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# получить удалить
class CategoryRetriveUpdateDestroy(RetriveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



# 1создание категории
class CategoryCreateAPIView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



# получение одной категории
class CategoryRetrieveAPIView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer




class CategoryDestroyAPIView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Listing
from .serializers import ListingSerializer


# 1. чтение для всех
@api_view(['GET'])
def listing_list(request):
    listings = Listing.objects.filter(is_active=True)
    serializer = ListingSerializer(listings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    serializer = ListingSerializer(listing)
    return Response(serializer.data)


# 2. создание — только админ
@api_view(['POST'])
@permission_classes([IsAdminUser])
def listing_create(request):
    serializer = ListingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3. редактирование и удаление — только админ
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def listing_update_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if request.method == 'PUT':
        serializer = ListingSerializer(listing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        listing.delete()
        return Response({'message': 'Объявление удалено'}, status=status.HTTP_204_NO_CONTENT)