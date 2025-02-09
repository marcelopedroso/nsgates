#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ

env = environ.Env()
environ.Env.read_env()  # Lê o arquivo .env

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

# Define a porta padrão como 8000 caso API_PORT não esteja definida no .env
API_PORT = env('API_PORT', default='8000')

if __name__ == '__main__':
    if 'runserver' in sys.argv and not any(f':{API_PORT}' in arg for arg in sys.argv):
        sys.argv.append(f'0.0.0.0:{API_PORT}')
    main()
