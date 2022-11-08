from django.contrib import admin
from django.urls import path, include
from game.views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/user/', include('users.api.urls')),
    path('api/game/', include('game.api.urls')),
    
    path('game/',game_view, name='game-page'),
    path('game/invite', game_invite_handler, name='game-invite-handler'),
    path('game/live/<int:game_id>/', game_live_view, name='game-live-view'),
    path('game/<int:game_id>/', game_review, name='game-review'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
