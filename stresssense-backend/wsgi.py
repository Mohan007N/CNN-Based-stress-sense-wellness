"""
wsgi.py — WSGI Entry Point for Production Deployment
=====================================================
Used by gunicorn / uWSGI to locate the Flask app object.

Deployment commands:
    gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4

Render / Railway will auto-detect this file via the Procfile.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
