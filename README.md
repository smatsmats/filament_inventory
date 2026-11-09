# Filament Tracker (Django)

Track 3D-printer filament rolls: Brand, Store Code, Make Code, Model, Type,
Quantity (grams), Price, Price / gram (auto-calculated), Texture, Color, NFC,
Source, Bought, Used-up, Notes. Login required; add/edit/delete/search in the UI,
bulk management in `/admin/`.

## Run locally
    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    export DJANGO_DEBUG=1
    .venv/bin/python manage.py migrate
    .venv/bin/python manage.py createsuperuser
    .venv/bin/python manage.py runserver

Tests: `DJANGO_DEBUG=1 .venv/bin/python manage.py test`

## Google Cloud Run
Cloud Run's filesystem is ephemeral, so production uses Cloud SQL (Postgres) via `DATABASE_URL`.
The container runs `migrate` on startup.

    PROJECT=your-project REGION=us-west1
    gcloud config set project $PROJECT
    gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

    # Database
    gcloud sql instances create filaments-db --database-version=POSTGRES_16 --tier=db-f1-micro --region=$REGION
    gcloud sql databases create filaments --instance=filaments-db
    DBPASS=$(openssl rand -hex 16)
    gcloud sql users create filaments --instance=filaments-db --password=$DBPASS

    # Secrets
    openssl rand -hex 32 | gcloud secrets create filament-secret-key --data-file=-
    printf "postgres://filaments:$DBPASS@/filaments?host=/cloudsql/$PROJECT:$REGION:filaments-db" | gcloud secrets create filament-database-url --data-file=-
    SA=$(gcloud projects describe $PROJECT --format='value(projectNumber)')-compute@developer.gserviceaccount.com
    for s in filament-secret-key filament-database-url; do
      gcloud secrets add-iam-policy-binding $s --member=serviceAccount:$SA --role=roles/secretmanager.secretAccessor
    done
    gcloud projects add-iam-policy-binding $PROJECT --member=serviceAccount:$SA --role=roles/cloudsql.client

    # Deploy (the app has its own login, so public ingress is fine)
    gcloud run deploy filament-tracker --source . --region=$REGION --allow-unauthenticated \
      --add-cloudsql-instances=$PROJECT:$REGION:filaments-db \
      --set-secrets=DJANGO_SECRET_KEY=filament-secret-key:latest,DATABASE_URL=filament-database-url:latest

Create the first user (one time), using the Cloud SQL Auth Proxy locally:

    cloud-sql-proxy $PROJECT:$REGION:filaments-db --port 5433 &
    DATABASE_URL="postgres://filaments:$DBPASS@127.0.0.1:5433/filaments" DJANGO_SECRET_KEY=x .venv/bin/python manage.py createsuperuser

Then browse to the service URL and log in. Health check: `/healthz`.

### Stop / tear down
    gcloud run services remove-iam-policy-binding filament-tracker --region=$REGION --member=allUsers --role=roles/run.invoker   # block public access
    gcloud run services add-iam-policy-binding filament-tracker --region=$REGION --member=allUsers --role=roles/run.invoker      # unblock
    gcloud run services delete filament-tracker --region=$REGION
    gcloud sql instances delete filaments-db   # deletes all data; the instance bills while it exists

## Env vars
`DJANGO_SECRET_KEY` (required unless `DJANGO_DEBUG=1`), `DATABASE_URL` (default: local SQLite),
`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` (comma separated), `PORT`.
