from django import forms
from apps.telegrambot.models import TelegramBot


class BotTokenForm(forms.ModelForm):
    class Meta:
        model = TelegramBot
        fields = ["token", "name", "user", "webhook_url", "is_active"]

    def clean_token(self):
        token = self.cleaned_data.get("token")
        # Add any custom validation for the token here
        return token

    def clean_webhook_url(self):
        url = self.cleaned_data.get("webhook_url")
        if not url.startswith("https://"):
            raise forms.ValidationError("Webhook URL must use HTTPS protocol")
        return url
