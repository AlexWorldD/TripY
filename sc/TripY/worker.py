from __future__ import absolute_import
from TripY.celery import app
from .entity import Entity


app.conf.CELERY_ALWAYS_EAGER = True
app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


@app.task(bind=True, default_retry_delay=10)
def parse_link_h(self, url, key, geo_id):
    try:
        entity = Entity(url, key, geo_id)
        self.update_state(state="PROGRESS", meta={'progress': 20})
        entity.collect_main_info()
        self.update_state(state="PROGRESS", meta={'progress': 50})
        entity.dictify()
        return entity.success
    except Exception as exc:
        raise self.retry(exc=exc)


# @app.task(bind=True, default_retry_delay=10)
# def parse_link_r(self, url, key):
#     try:
#         entity = Entity(url, key)
#         entity.collect_main_info()
#         entity.dictify()
#         return entity.success
#     except Exception as exc:
#         raise self.retry(exc=exc)
#
#
# @app.task(bind=True, default_retry_delay=10)
# def parse_link_a(self, url, key):
#     try:
#         entity = Entity(url, key)
#         entity.collect_main_info()
#         entity.dictify()
#         return entity.success
#     except Exception as exc:
#         raise self.retry(exc=exc)
