import calendar
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


def somar_meses(data_base, meses):
    """Soma uma quantidade de meses a uma data, ajustando o dia se o mês destino for mais curto."""
    mes_index = data_base.month - 1 + meses
    ano = data_base.year + mes_index // 12
    mes = mes_index % 12 + 1
    ultimo_dia_do_mes = calendar.monthrange(ano, mes)[1]
    dia = min(data_base.day, ultimo_dia_do_mes)
    return date(ano, mes, dia)


class Conta(models.Model):
    TIPO_CHOICES = [
        ('corrente', 'Conta Corrente'),
        ('poupanca', 'Poupança'),
        ('carteira', 'Carteira'),
        ('cartao', 'Cartão de Crédito'),
    ]

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='corrente')
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def saldo_atual(self):
        receitas = self.lancamentos.filter(tipo='receita').aggregate(total=Sum('valor'))['total'] or 0
        despesas = self.lancamentos.filter(tipo='despesa').aggregate(total=Sum('valor'))['total'] or 0
        return self.saldo_inicial + receitas - despesas


class Categoria(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    nome = models.CharField(max_length=60)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='despesa')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'categorias'
        unique_together = ('nome', 'tipo')

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'


class Lancamento(models.Model):
    """Uma movimentação financeira: uma receita, ou uma despesa (à vista ou parcelada)."""

    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='lancamentos')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='lancamentos')
    descricao = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='despesa')
    data = models.DateField(help_text='Data da compra/recebimento (a 1ª parcela vence nesta data).')
    parcelado = models.BooleanField(default=False)
    numero_parcelas = models.PositiveIntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'

    def clean(self):
        if self.parcelado and self.numero_parcelas < 2:
            raise ValidationError('Um lançamento parcelado precisa de pelo menos 2 parcelas.')
        if not self.parcelado and self.numero_parcelas != 1:
            raise ValidationError('Lançamentos não parcelados devem ter exatamente 1 parcela.')

    def save(self, *args, **kwargs):
        if not self.parcelado:
            self.numero_parcelas = 1
        is_novo = self.pk is None
        super().save(*args, **kwargs)
        if is_novo:
            self.gerar_parcelas()

    def gerar_parcelas(self):
        """Divide o valor total em N parcelas mensais, uma a partir da data do lançamento."""
        valor_parcela = round(self.valor / self.numero_parcelas, 2)
        diferenca_arredondamento = self.valor - (valor_parcela * self.numero_parcelas)

        novas_parcelas = []
        for numero in range(1, self.numero_parcelas + 1):
            valor_desta_parcela = valor_parcela
            if numero == self.numero_parcelas:
                valor_desta_parcela += diferenca_arredondamento
            novas_parcelas.append(Parcela(
                lancamento=self,
                numero=numero,
                valor=valor_desta_parcela,
                data_vencimento=somar_meses(self.data, numero - 1),
            ))
        Parcela.objects.bulk_create(novas_parcelas)


class Parcela(models.Model):
    """Cada parcela de um lançamento, com sua própria data de vencimento e status de pagamento."""

    lancamento = models.ForeignKey(Lancamento, on_delete=models.CASCADE, related_name='parcelas')
    numero = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    paga = models.BooleanField(default=False)

    class Meta:
        ordering = ['data_vencimento', 'numero']
        unique_together = ('lancamento', 'numero')

    def __str__(self):
        return f'{self.lancamento.descricao} - Parcela {self.numero}/{self.lancamento.numero_parcelas}'


class Orcamento(models.Model):
    """Limite de gasto planejado para uma categoria em um mês/ano específico."""

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='orcamentos')
    mes = models.PositiveSmallIntegerField()
    ano = models.PositiveSmallIntegerField()
    valor_limite = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-ano', '-mes']
        unique_together = ('categoria', 'mes', 'ano')

    def __str__(self):
        return f'{self.categoria.nome} - {self.mes:02d}/{self.ano} (limite R$ {self.valor_limite})'

    def clean(self):
        if not 1 <= self.mes <= 12:
            raise ValidationError('Mês deve estar entre 1 e 12.')

    @property
    def valor_gasto(self):
        """Soma as parcelas da categoria que vencem neste mês/ano (independente de quando a compra foi feita)."""
        total = Parcela.objects.filter(
            lancamento__categoria=self.categoria,
            lancamento__tipo='despesa',
            data_vencimento__year=self.ano,
            data_vencimento__month=self.mes,
        ).aggregate(total=Sum('valor'))['total']
        return total or 0

    @property
    def percentual_usado(self):
        if self.valor_limite == 0:
            return 0
        return round((self.valor_gasto / self.valor_limite) * 100, 1)

    @property
    def estourado(self):
        return self.valor_gasto > self.valor_limite
