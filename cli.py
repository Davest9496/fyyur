from flask import Flask
from flask_migrate import Migrate
from models import db


def register_commands(app):
    """Register Flask-Migrate commands"""
    migrate = Migrate(app, db)


# If you want to run migrations from this file directly
if __name__ == '__main__':
    from app import app
    register_commands(app)
    print("CLI commands registered")
