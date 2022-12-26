from django import forms
from lottery.models import BettingAgency

class BettingAgencyEditForm(forms.ModelForm):
    class Meta:
        model = BettingAgency
        fields = ('name', 'system_commission', 'is_active',)