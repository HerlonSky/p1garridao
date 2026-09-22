from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('lancamentos/', views.lancamento_lista, name='lancamento_lista'),
    path('lancamentos/novo/', views.lancamento_criar, name='lancamento_criar'),
    path('orcamentos/', views.orcamento_lista, name='orcamento_lista'),
    path('orcamentos/novo/', views.orcamento_criar, name='orcamento_criar'),
    path('parcelas/', views.parcela_lista, name='parcela_lista'),
    path('parcelas/<int:pk>/marcar-paga/', views.parcela_marcar_paga, name='parcela_marcar_paga'),
]
