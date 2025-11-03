from flask_migrate import MigrateCommand
from flask.cli import FlaskGroup
from app import create_app, db
import click

app = create_app()
cli = FlaskGroup(create_app=create_app)

@cli.command("seed")
def seed():
    from seed import run_seed
    run_seed(app)

if __name__ == "__main__":
    cli()
