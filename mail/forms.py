from django.forms import ModelForm
from .models import Mail

class NewMailForm(ModelForm):
	class Meta:
		model = Mail
		fields = ['sent_to', 'subject', 'content']