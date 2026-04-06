from django.apps import AppConfig

class MappingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mapping'

    def ready(self):
        """
        Runs when the Django server starts.
        """
        # Delaying slightly to allow the server to fully initialize
        import threading
        import sys
        from .openhim.register import register_mediator
        
        # Only register if we are running the server
        if 'runserver' in sys.argv:
            threading.Timer(5.0, register_mediator).start()
