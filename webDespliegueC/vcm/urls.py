from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^$', views.autenticacion, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^usuario_create/$', views.usuario_create, name='usuario_create'),
    url(r'^concurso_create/$', views.concurso_crate, name='concurso_create'),
    url(r'^concurso_update/(?P<pk>\d+)$', views.concurso_update, name='concurso_update'),
    url(r'^concurso_videos/(?P<pk>\d+)$', views.concurso_videos, name='concurso_videos'),
    url(r'^participar/(?P<concurso_url>[\w.@+-]+)/$', views.participar, name='participar'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)