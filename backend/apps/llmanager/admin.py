from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import LLMProviderConfig

admin.site.register(LLMProviderConfig, SingletonModelAdmin)
