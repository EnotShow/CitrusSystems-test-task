from django.urls import path

from api.views.auth import register, login
from api.views.game import refill, create_game, buy_game, refund

urlpatterns = [
    # auth operations
    path('registration/', register, name='register'),
    path('token/', login, name='login'),
    # game operations
    path('game/create/', create_game, name='create_game'),
    path('game/buy/', buy_game, name='buy_game'),
    # balance operations
    path('deposit/', refill, name='refill'),
    path('rollback/', refund, name='refund'),
]
