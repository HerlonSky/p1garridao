from django import forms

from .models import Lancamento, Orcamento


class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = ['conta', 'categoria', 'descricao', 'valor', 'tipo', 'data', 'parcelado', 'numero_parcelas']
        widgets = {
            'conta': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parcelado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_parcelas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        parcelado = cleaned_data.get('parcelado')
        numero_parcelas = cleaned_data.get('numero_parcelas')

        if parcelado and (not numero_parcelas or numero_parcelas < 2):
            self.add_error('numero_parcelas', 'Informe pelo menos 2 parcelas para um lançamento parcelado.')
        if not parcelado:
            cleaned_data['numero_parcelas'] = 1
        return cleaned_data


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['categoria', 'mes', 'ano', 'valor_limite']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'mes': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '12'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_limite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }
