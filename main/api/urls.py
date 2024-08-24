from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('', views.getRoutes),
    path('user/<int:pk>', views.getUser),
    path('register', views.register),
    path('notes', views.getNote),
    path('create_note', views.create_note),
    path('delete_note/<int:pk>', views.delete_note),


    # Refresh and Access Token url
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Game Url
    path('cards', views.card),
    path('characters', views.character),
    path('create_avatar', views.create_avatar),
    # path('player_card', views.player_card),
    path('get_player', views.get_player),
    path('get_card/<int:pk>', views.get_card),
    path('update_player', views.update_player_card),
    path('get_character/<int:pk>', views.get_character),
    
    # Match Url
    path('game/match', views.match),
    path('game/match_request', views.requestMatch),
    path('game/find_match', views.FindMatch),
    path('game/accept_match/<int:pk>/', views.AcceptMatch),
    path('match/<int:pk>', views.matchDetail, name='matchDetail'),
    path('game/match_status/', views.match_status, name="match_status"),
    path('game/pending_matches/', views.pending_matches, name='pending_matches')
]