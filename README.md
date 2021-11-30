# Currency Exchange Calculator
REST API service for currency exchange calculator


## Installing with Pipenv
```sh
# Clone the repo
$ git clone ....

# Install packages with pipenv
$ pipenv install
```

## Flask CLI help command output:
Flask Commands:
```
db      Perform database migrations.
routes  Show the routes for the app.
run     Run a development server.
seed    Populate initial data from CSV file.
shell   Run a shell in the app context.
```

## Environment
To setup application environment you have to create environment variables
```
set FLASK_APP=calc.py
set FLASK_ENV=dev
 
```
or create file .env of this content:
```
FLASK_APP=calc
FLASK_CONFIG=prod
```

## Running
```sh
$ pipenv shell

# (Optional for development, recommended)
$ flask db init # Initializes a new database.
$ flask db migrate # Creates the alembic tables in the database.

$ flask db upgrade # Creates the model tables in the database.

# To populate initial data from file:
$ flask seed exchange.csv

# Run the app
$ flask run
```


## Swagger documentation
```
http://127.0.0.1:5000/api/v1/currency/swagger.json
```

## Endpoint that returns historical data for specified currency pair.
```
http://127.0.0.1:5000/api/v1/currency/pairs/{pair_id}/history
eg. http://127.0.0.1:5000/api/v1/currency/pairs/1/history
```

## Endpoint that calculate rate for given currency pair at given date. 
In case there is no such currency pair, you need to calculate it by using others, for example for input NZD/AUD you can calculate rate by converting NZD -> USD -> AUD. If there are couple of variations we need minimal rate.

```
http://127.0.0.1:5000/api/v1/currency/rates/{base_code}/{target_code}/{date}
eg. http://127.0.0.1:5000/api/v1/currency/rates/NZD/AUD/2020-01-02
```
