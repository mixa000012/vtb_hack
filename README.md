# vtb_hack

## Deploy

For local development:

```
docker compose -f docker-compose_example.yaml up -d
```

Cube and EarthDistance extensions must be enabled in postgreSQL BD, so log in database using pgsql and install
extensions:

```   
-- Log in to PostgreSQL database using psql
psql -U <username> -d <database_name>

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS cube;
CREATE EXTENSION IF NOT EXISTS earthdistanc
```

## Used technology

* Python 3.10;
* Docker and Docker Compose;
* PostgreSQL;
* SQLAlchemy;
* Alembic;