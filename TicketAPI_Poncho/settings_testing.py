from .settings import * 


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Channels en memoria 'group_send()' que se dispara al crear evento/ticket
# funciona sin Redis ni un consumer WebSocket vivo.
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

DEBUG = False