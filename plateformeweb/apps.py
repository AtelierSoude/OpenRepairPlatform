

from django.apps import AppConfig, apps

class PlateformeWebAppConfig(AppConfig):
    name = 'plateformeweb'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Organization'))
        registry.register(self.get_model('Place'))
        CustomUser = apps.get_model('users', 'CustomUser')
        registry.register(CustomUser)


