from __future__ import absolute_import
from TripY.celery import app
from .entity import Entity

# app.conf.CELERY_ALWAYS_EAGER = True
# app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


@app.task(bind=True, default_retry_delay=10)
def parse_link(self, url, key):
    try:
        entity = Entity(url, key)
        entity.collect_main_info()
        entity.dictify()
        return entity.success
    except Exception as exc:
        raise self.retry(exc=exc)
