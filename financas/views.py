from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LancamentoForm, OrcamentoForm
from .models import Conta, Lancamento, Orcamento, Parcela


def dashboard(request):
    hoje = date.today()
    contas = Conta.objects.all()
    orcamentos_do_mes = Orcamento.objects.filter(mes=hoje.month, ano=hoje.year).select_related('categoria')
    ultimos_lancamentos = Lancamento.objects.select_related('conta', 'categoria')[:10]
    parcelas_em_aberto = Parcela.objects.filter(paga=False).select_related('lancamento').order_by('data_vencimento')[:10]

    return render(request, 'financas/dashboard.html', {
        'contas': contas,
        'orcamentos_do_mes': orcamentos_do_mes,
        'ultimos_lancamentos': ultimos_lancamentos,
        'parcelas_em_aberto': parcelas_em_aberto,
        'mes_atual': hoje.month,
        'ano_atual': hoje.year,
    })


def lancamento_lista(request):
    lancamentos = Lancamento.objects.select_related('conta', 'categoria').prefetch_related('parcelas')
    return render(request, 'financas/lancamento_lista.html', {'lancamentos': lancamentos})


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
