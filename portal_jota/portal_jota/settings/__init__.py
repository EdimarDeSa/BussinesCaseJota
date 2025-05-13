import os

ENV_TYPE = os.getenv("ENV_TYPE", "full").lower()

match ENV_TYPE:
    case "web":
        from .web import *
    case "beat":
        from .beat import *
    case "worker":
        from .worker import *
    case "full":
        from .full import *
