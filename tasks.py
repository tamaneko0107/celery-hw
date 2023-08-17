from celery import Celery, Task
import config as cfg
import time


# Celery configuration
celery = Celery(__name__, broker=cfg.CELERY_BROKER_URL, backend=cfg.CELERY_RESULT_BACKEND)

# Celery task decorator
@celery.task(bind=True)
def progress_task(self, input_value):
    for i in range(input_value):
        self.update_state(state='PROGRESS', meta={'current': i, 'total': input_value})
        time.sleep(1)
        print(f'{i}/{input_value}')
    return 'done'

# Celery task class
class ProgressTask(Task):
    def run(self, input_value):
        for i in range(input_value*2):
            self.update_state(state='PROGRESS', meta={'current': i, 'total': input_value*2})
            time.sleep(1)
            print(f'{i}/{input_value*2}')
        return 'done'

progress_task_class = celery.register_task(ProgressTask())