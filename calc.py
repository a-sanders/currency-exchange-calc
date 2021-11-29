import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

##

import click
from flask_migrate import Migrate
from app import create_app, db

# Import models
from app.models.currency import CurrencyPair, CurrencyRate


app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.cli.command()
@click.argument("fd", metavar="filename", type=click.File('r'))
@click.option("-d", "--dry-run", default=False, is_flag=True, help="Simulate importing process")
@click.option("-p", "--pairs-only", default=False, is_flag=True, help="Populate currency pairs only")
def seed(fd, dry_run=False, pairs_only=False):
    """ Populate initial data from CSV file.

        The input file should has at least two columns:

            Date, pair

        The first row should be a header. The pair column should be named in format <base code>/<target code>

            eg. Date,EUR/USD,USD/CHF,USD/CAD,EUR/GBP,EUR/JPY,EUR/CHF,AUD/USD,GBP/JPY
    """
    import csv
    from datetime import datetime
    from sqlalchemy.exc import SQLAlchemyError

    sniffer = csv.Sniffer()
    sample = fd.read(1024)
    fd.seek(0)
    dialect = sniffer.sniff(sample)
    has_header = sniffer.has_header(sample)
    if not has_header:
        click.echo("ERROR: the first line of the input file should be a header in format "
                   "\"Date,pair1,pair2,...pairN\"", err=True)

    reader = csv.DictReader(fd, dialect=dialect)

    with app.app_context():
        #db.metadata.create_all(db.engine)

        click.echo("\nImporting currency pairs: ")
        codes = reader.fieldnames[1:]
        for i, code in enumerate(codes):
            click.echo(f"#{i+1}\t{code}\t\t", nl=False)
            base_code, target_code = code.split("/")
            if pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first():
                click.echo(f"{pair} already exists")
                continue

            try:
                pair = CurrencyPair(base_code=base_code, target_code=target_code)
                db.session.add(pair)
                if not dry_run:
                    db.session.commit()
                click.echo(f"{pair} added")
            except SQLAlchemyError as e:
                click.echo(f"EXCEPTION: {e}", err=True)
                db.session.rollback()

        if pairs_only:
            return

        click.echo("\nImporting currency exchange rates: ")
        for row in reader:
            click.echo(f"Row #{reader.line_num} - {row}")

            date = row.pop('Date')
            d = datetime.strptime(date, "%Y-%m-%d").date()

            click.echo(f"\tDate: {date}")
            for code, r in row.items():
                click.echo(f"\t\t{code}\t{r}\t\t", nl=False)
                base_code, target_code = code.split("/")
                if not (pair := CurrencyPair.query.filter_by(base_code=base_code, target_code=target_code).first()):
                    click.echo(f"Currency Pair {code} not found!", err=True)
                    continue
                if rate := CurrencyRate.query.filter_by(date=d, pair_id=pair.id).first():
                    click.echo(f"{rate} is already exists")
                    continue
                try:
                    rate = CurrencyRate(date=d, rate=r, pair=pair)
                    db.session.add(rate)
                    if not dry_run:
                        db.session.commit()
                    click.echo(f"{rate} added")
                except SQLAlchemyError as e:
                    click.echo(f"EXCEPTION: {e}", err=True)
                    db.session.rollback()
    click.echo("Done.")


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, CurrencyPair=CurrencyPair, CurrencyRate=CurrencyRate)

