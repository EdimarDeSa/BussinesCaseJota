import os

from .base import *  # noqa: F403

ENV_TYPE = os.getenv("ENV_TYPE", "full").lower()

match ENV_TYPE:
    case "web":
        from .web import *  # noqa: F403
    case "beat":
        from .beat import *  # noqa: F403
    case "worker":
        from .celery import *  # noqa: F403
    case "full":
        from .full import *  # noqa: F403
