from django.urls import path
from django.views.decorators.cache import cache_page

from .views import AboutAuthorView, AboutTechView

app_name = 'about'

urlpatterns = [
    path('author/', cache_page(60 * 60 * 24)(
        AboutAuthorView.as_view()), name='author'
    ),
    path('tech/', cache_page(60 * 60 * 24)(
        AboutTechView.as_view()), name='tech'
    ),
]
