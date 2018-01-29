from __future__ import absolute_import
from TripY.celery import app
from .entity import Entity
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# app.conf.CELERY_ALWAYS_EAGER = True
# app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


@app.task(bind=True, default_retry_delay=10, reply_to='results')
def parse_link(self, url, key, geo_id, reviews):
    try:
        entity = Entity(url, key, geo_id, reviews)
        entity.collect_main_info()
        # self.update_state(state="PROGRESS", meta={'progress': 50})
        if entity.success:
            entity.dictify()
            print(bcolors.OKGREEN+'Insert to DB: Success'+bcolors.ENDC)
        return entity.success
    except Exception as exc:
        raise self.retry(exc=exc)

