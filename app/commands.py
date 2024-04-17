import click
from flask.cli import with_appcontext
from helper.helper import populate_tables, clear_all_records

def register_commands(app):
    @app.cli.command('populate-db')
    @with_appcontext
    def seed_db_command():
        """Populates the database with initial data."""
        populate_tables()
        click.echo('Database has been populated.')

    @app.cli.command('clear-db')
    @with_appcontext
    def clear_db():
        clear_all_records()
        click.echo('All records in all tables are cleared.')