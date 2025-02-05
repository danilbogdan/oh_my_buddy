import requests
from django.contrib import admin, messages

from apps.telegrambot.models import Conversation, ConversationMessage, Lead, TelegramBot
from apps.telegrambot.services import build_webhook_url, register_webhook


class BotAdmin(admin.ModelAdmin):
    list_display = ("token", "name", "user", "is_active", "webhook_url")
    search_fields = (
        "token",
        "name",
    )
    readonly_fields = ("webhook_url",)
    raw_id_fields = ("user",)
    actions = ["fetch_webhook_info"]

    def fetch_webhook_info(self, request, queryset):
        for obj in queryset:
            if not obj.token:
                self.message_user(request, f"No token provided for bot {obj.name}", level=messages.ERROR)
                continue
            try:
                response = requests.get(f"https://api.telegram.org/bot{obj.token}/getWebhookInfo")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        info = data.get("result", {})
                        self.message_user(
                            request,
                            f"Bot {obj.name} - URL: {info.get('url', 'Not set')}, Pending updates: {info.get('pending_update_count', 0)}",
                            level=messages.SUCCESS,
                        )
                    else:
                        self.message_user(
                            request,
                            f"Bot {obj.name} - Error: {data.get('description', 'Unknown error')}",
                            level=messages.ERROR,
                        )
                else:
                    self.message_user(
                        request, f"Bot {obj.name} - HTTP Error: {response.status_code}", level=messages.ERROR
                    )
            except Exception as e:
                self.message_user(
                    request, f"Bot {obj.name} - Error fetching webhook info: {str(e)}", level=messages.ERROR
                )

    fetch_webhook_info.short_description = "Fetch webhook info for selected bots"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.refresh_from_db()
        try:
            webhook_url = build_webhook_url(request, obj)
            result = register_webhook(obj.token, webhook_url)
            if result.get("ok"):
                messages.success(request, f"Webhook successfully registered for bot {obj.name}")
                obj.webhook_url = webhook_url
                obj.save(update_fields=["webhook_url"])
            else:
                messages.error(request, f"Failed to register webhook: {result.get('description')}")
        except Exception as e:
            messages.error(request, f"Error registering webhook: {str(e)}")


class MessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("message", "author", "created_at")


class ConversationAdmin(admin.ModelAdmin):
    list_display = ("bot", "chat_id", "created_at")
    search_fields = ("bot__name", "chat_id")
    inlines = [MessageInline]
    readonly_fields = ("created_at",)


admin.site.register(TelegramBot, BotAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Lead)
