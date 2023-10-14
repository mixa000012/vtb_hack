# vtb_hack

## Deploy

For local development:

```
docker compose -f docker-compose_example.yaml up -d
```

Cube and EarthDistance extensions must be enabled in postgreSQL BD, so log in database using pgsql and install
extensions:

```   
create extension cube;
create extension earthdistance;
```

## Used technology

* Python 3.10;
* Docker and Docker Compose;
* PostgreSQL;
* SQLAlchemy;
* Alembic;