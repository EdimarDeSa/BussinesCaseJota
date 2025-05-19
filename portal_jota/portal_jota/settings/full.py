from django.conf import settings

from .beat import *
from .celery import *

CELERY_TASK_ALWAYS_EAGER = settings.DEBUG
CELERY_TASK_EAGER_PROPAGATES = settings.DEBUG

from .web import *
