from datetime import date

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LancamentoForm, OrcamentoForm
from .models import Categoria, Conta, Lancamento, Orcamento, Parcela


def dashboard(request):
    hoje = date.today()
    contas = Conta.objects.all()
    orcamentos_do_mes = Orcamento.objects.filter(mes=hoje.month, ano=hoje.year).select_related('categoria')
    ultimos_lancamentos = Lancamento.objects.select_related('conta', 'categoria')[:10]
    parcelas_em_aberto_qs = Parcela.objects.filter(paga=False).select_related('lancamento').order_by('data_vencimento')

    saldo_total = sum((conta.saldo_atual for conta in contas), 0)

    receitas_mes = Lancamento.objects.filter(
        tipo='receita', data__year=hoje.year, data__month=hoje.month,
    ).aggregate(total=Sum('valor'))['total'] or 0

    despesas_mes = Parcela.objects.filter(
        lancamento__tipo='despesa', data_vencimento__year=hoje.year, data_vencimento__month=hoje.month,
    ).aggregate(total=Sum('valor'))['total'] or 0

    return render(request, 'financas/dashboard.html', {
        'contas': contas,
        'orcamentos_do_mes': orcamentos_do_mes,
        'ultimos_lancamentos': ultimos_lancamentos,
        'parcelas_em_aberto': parcelas_em_aberto_qs[:10],
        'mes_atual': hoje.month,
        'ano_atual': hoje.year,
        'saldo_total': saldo_total,
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'total_parcelas_em_aberto': parcelas_em_aberto_qs.count(),
        'orcamentos_estourados': sum(1 for o in orcamentos_do_mes if o.estourado),
    })


def lancamento_lista(request):
    lancamentos = Lancamento.objects.select_related('conta', 'categoria').prefetch_related('parcelas')

    # Feature 1: busca por descrição + filtro por categoria (podem ser usados juntos ou separados)
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')

    # Desafio extra: as duas condições são combinadas num único objeto Q() e aplicadas
    # numa só chamada de .filter(). Q() vazio não filtra nada; "&=" junta as condições
    # com AND, então com os dois preenchidos o SQL fica: WHERE descricao LIKE ... AND categoria_id = ...
    filtros = Q()
    if q:
        filtros &= Q(descricao__icontains=q)
    if categoria_id.isdigit():
        filtros &= Q(categoria_id=categoria_id)
    lancamentos = lancamentos.filter(filtros)

    return render(request, 'financas/lancamento_lista.html', {
        'lancamentos': lancamentos,
        'categorias': Categoria.objects.all(),
        'categoria_id': categoria_id,
        'filtrando': bool(q or categoria_id),
    })


def lancamento_criar(request):
    if request.method == 'POST':
        form = LancamentoForm(request.POST)
        if form.is_valid():
            lancamento = form.save()
            if lancamento.parcelado:
                messages.success(
                    request,
                    f'Lançamento criado e dividido em {lancamento.numero_parcelas} parcelas automaticamente.',
                )
            else:
                messages.success(request, 'Lançamento criado com sucesso.')
            return redirect('lancamento_lista')
    else:
        form = LancamentoForm()
    return render(request, 'financas/lancamento_form.html', {'form': form})


def orcamento_lista(request):
    orcamentos = Orcamento.objects.select_related('categoria')
    return render(request, 'financas/orcamento_lista.html', {'orcamentos': orcamentos})


def orcamento_criar(request):
    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orçamento criado com sucesso.')
            return redirect('orcamento_lista')
    else:
        form = OrcamentoForm()
    return render(request, 'financas/orcamento_form.html', {'form': form})


def parcela_lista(request):
    parcelas = Parcela.objects.select_related('lancamento', 'lancamento__categoria')
    return render(request, 'financas/parcela_lista.html', {'parcelas': parcelas})


def parcela_marcar_paga(request, pk):
    parcela = get_object_or_404(Parcela, pk=pk)
    parcela.paga = not parcela.paga
    parcela.save(update_fields=['paga'])
    return redirect('parcela_lista')
