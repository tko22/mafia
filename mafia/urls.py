"""mafia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from mafiaapp import views

urlpatterns = [
    #/admin
    url(r'^admin/', admin.site.urls),
    #/
    url(r'^$',views.index, name='index'),
    #/abcde/
    url(r'^(?P<game_id>\w+)/$', views.lobby,name='lobby'),
    #/abcde/game/
    url(r'^(?P<game_id>\w+)/game/$', views.ingame, name='ingame'),
    url(r'^api/createlobby', views.createlobby, name='createlobby'),
    url(r'^api/joinlobby', views.joinlobby, name='joinlobby'),
    url(r'^api/removeuser', views.removeuser, name='removeuser'),
    url(r'^api/startgame', views.startgame, name='startgame'),
    url(r'^api/endround',views.endround, name='endround'),
    url(r'^api/leavegame',views.leavegame, name='leavegame'),
    url(r'^api/getusers',views.getusers,name='getusers'),
    url(r'^api/getround',views.getround,name='getround'),
    url(r'^api/leavelobby',views.leavelobby,name='leavelobby'),
    url(r'^api/startround',views.startround,name='startround'),
]
