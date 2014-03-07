from django.apps import AppConfig


class RulesConfig(AppConfig):
    name = 'rules'


class AutodiscoverRulesConfig(RulesConfig):
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('rules')
