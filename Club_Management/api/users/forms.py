from django import forms


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Your email', max_length=255)
