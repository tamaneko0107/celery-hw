from flask import Flask, request
from celery.app.control import Inspect
from flask_restx import Api, Resource, fields, Namespace
import config as cfg
from tasks import progress_task, progress_task_class, celery

# Flask configuration
app = Flask(__name__)
app.config.from_object(cfg)

# Flask-RestX configuration
api = Api(app, version='1.0', title='Celery API', description='A simple Celery API', doc='/docs')


celery_ns = Namespace('Celery', description='Celery operations')
api.add_namespace(celery_ns, path='/celery')

celery_result_ns = Namespace('Celery Result', description='Celery result operations')
api.add_namespace(celery_result_ns, path='/celery_result')


# Flask-RestX models
task_model = celery_ns.model('Task', {
    'input_value': fields.Integer(required=True, description='The input value for the task', default=5)
})


# Flask-RestX routes
@celery_ns.route('/start_task_post')
class StartTask(Resource):
    @celery_ns.expect(task_model)
    def post(self):
        input_value = celery_ns.payload['input_value']
        if input_value <= 0:
            return {'error': 'Input value must be positive integer.'}, 400
        task = progress_task.delay(input_value)
        return {'task_id': task.id}
    

@celery_ns.route('/start_task_get')
class StartTask(Resource):
    @celery_ns.doc(params={'input_value': 'The input value for the task'})
    def get(self):
        input_value = int(request.args.get('input_value', 5))
        if input_value <= 0:
            return {'error': 'Input value must be positive integer.'}, 400
        task = progress_task_class.apply_async(args=[input_value])
        return {'task_id': task.id}


@celery_result_ns.route('/task_progress')
class TaskProgress(Resource):
    @celery_result_ns.doc(params={'task_id': 'The task id'})
    def get(self):
        result = celery.AsyncResult(request.args.get('task_id'))
        return {'state': result.state, 'progress': result.info}

@celery_result_ns.route('/tasks')
class Tasks(Resource):
    def get(self):
        i = Inspect(app=celery)
        return i.active()

if __name__ == '__main__':
    app.run()
