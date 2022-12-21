from django import forms

# Limit orders generation form
class OrderForm(forms.Form):
    price = forms.FloatField(label='Price ($)')
    quantity = forms.FloatField(label='Quantity')

    def clean(self):
        cleaned_data = super().clean()
        price = self.cleaned_data.get('price')
        quantity = self.cleaned_data.get('quantity')
        if price < 0:
            raise forms.ValidationError('')  # display messages.error instead
        if quantity < 0:
            raise forms.ValidationError('')  # display messages.error instead
        return cleaned_data

# Market orders generation form
class MarketOrderForm(forms.Form):
    quantity = forms.FloatField(label='Quantity')

    def clean(self):
        cleaned_data = super().clean()
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError('')  # display messages.error instead
        return cleaned_data
