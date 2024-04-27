from django.urls import path
from . import views
# from transferapp.views import deleteTransfer

urlpatterns = [
    path('', views.index, name='index'),
    path('club', views.club, name='club'),
    path('clubDetalis/<str:param>/',views.clubDetalis,name='clubDetalis'),
    path('search', views.search, name='search'),
    path('players', views.players, name='players'),
    path('playersSearch', views.searchPlayer, name="playersSearch"),
    path('transfer', views.transfer, name="transfer"),
    path('addTransfer', views.addTransfer,name="addTransfer"),
    path('editTransfer', views.editTransfer, name="editTransfer"),
    path('updateTransfer', views.updateTransfer,name="updateTransfer"),
    path('deleteTransfer', views.deleteTransfer, name='deleteTransfer'),
    path('deleteAllTransfers',views.deleteAllTransfers,name='deleteAllTransfers')
    ]