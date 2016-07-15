web: gunicorn config.wsgi:application
worker: celery worker --app=metadata_schema_service.taskapp --loglevel=info
