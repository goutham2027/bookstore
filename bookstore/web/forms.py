from django import forms
from django.forms.widgets import DateTimeInput


class EmailForm(forms.Form):
    email = forms.EmailField(label="Email")
    subject = forms.CharField(label='Subject', max_length=100)
    body = forms.CharField(widget=forms.Textarea)
