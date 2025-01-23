from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import DefaultConfig, Conversation, Agent


admin.site.register(DefaultConfig, SingletonModelAdmin)
admin.site.register(Conversation)
admin.site.register(Agent)
