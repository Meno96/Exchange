from django import forms


class OrderForm(forms.Form):
    price = forms.FloatField(label='Price ($)')
    quantity = forms.FloatField(label='Quantity')

    def clean(self):
        cleanedData = super().clean()
        price = self.cleaned_data.get('price')
        quantity = self.cleaned_data.get('quantity')
        if price < 0:
            raise forms.ValidationError('')  # display messages.error instead
        if quantity < 0:
            raise forms.ValidationError('')  # display messages.error instead
        return cleanedData
