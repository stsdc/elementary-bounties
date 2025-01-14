# elementary Bounties ✨

This service adds bounty feature to the issues.

Only the issues that have label _confirmed_ get into Bounties database.

## Installation

### Dependency installations

To install the necessary packages:

```bash
poetry install
```

Poetry will create a virtual environment and install packages there.

### Setting up a SQLite3 Database

Database migrations are handled through Alembic. Migrations are for creating and uprading necessary tables in your database. The files generate by the migrations should be added to source control.

To setup a SQLite3 database for development (SQLite3 is usually **not** recommended for production unless you know what you are doing, use something like PostgreSQL or MySQL) navigate to the root folder and complete the following steps:

First, we need to initialize the database. Make sure you have a `.env` file in the root. Check `.env.template`.

Now that the app knows we want to use a SQLite database, run the following command to create it:

```zsh
alembic upgrade head
```

Finaly, run the API itself with the following command:

```zsh
uvicorn app.main:app --reload
```

### Test Webhooks locally

```zsh
docker run --network="host" --rm -it stripe/stripe-cli:latest listen --api-key sk_test_XXXXXX --forward-to localhost/stripe_hook
```

```zsh
docker run --network="host" ghcr.io/chmouel/gosmee:latest  client https://smee.io/imPbfItxHda72FK http://localhost:8000/webhook/github/issue
```
