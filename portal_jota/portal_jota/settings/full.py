from .base import *
from .base import DEBUG  # Para evitar erro de linter
from .beat import *
from .worker import *

CELERY_TASK_ALWAYS_EAGER = DEBUG
CELERY_TASK_EAGER_PROPAGATES = DEBUG

from .web import *
