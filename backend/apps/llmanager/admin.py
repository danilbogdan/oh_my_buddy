from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import LLMProviderConfig, LLModel, LLMProvider

admin.site.register(LLMProviderConfig, SingletonModelAdmin)
admin.site.register(LLModel)
admin.site.register(LLMProvider)
