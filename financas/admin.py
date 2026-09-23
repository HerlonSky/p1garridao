from django.contrib import admin

from .forms import LancamentoForm
from .models import Categoria, Conta, Lancamento, Orcamento, Parcela


class ParcelaInline(admin.TabularInline):
    model = Parcela
    extra = 0
    can_delete = False
    fields = ('numero', 'valor', 'data_vencimento', 'paga')
    readonly_fields = ('numero', 'valor', 'data_vencimento')


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'saldo_inicial', 'saldo_atual')
    list_filter = ('tipo',)
    search_fields = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nome',)


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    form = LancamentoForm  # reaproveita a validação do valor (> 0) também no Admin
    list_display = ('descricao', 'conta', 'categoria', 'tipo', 'valor', 'data', 'parcelado', 'numero_parcelas')
    list_filter = ('tipo', 'parcelado', 'categoria', 'conta')
    search_fields = ('descricao',)
    date_hierarchy = 'data'
    inlines = [ParcelaInline]


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'mes', 'ano', 'valor_limite', 'valor_gasto', 'percentual_usado', 'estourado')
    list_filter = ('ano', 'mes', 'categoria')


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('lancamento', 'numero', 'valor', 'data_vencimento', 'paga')
    list_filter = ('paga', 'data_vencimento')
    search_fields = ('lancamento__descricao',)
