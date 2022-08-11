from .app import create_app
from .utils.celery import celery_app as app


flask_app = create_app()


class ContextTask(app.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)


app.Task = ContextTask
