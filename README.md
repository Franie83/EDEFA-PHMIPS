# EF-PHMIPS

Full backend migration to Python Flask. React/Vite remains the frontend.

## Development
`cd backend && python -m venv .venv && pip install -r requirements.txt && python app.py`
Then in another terminal: `npm install && npm run dev`.

SQLite is the default development database. Set `DATABASE_URL` to PostgreSQL in production; SQLAlchemy uses JSONB on PostgreSQL.

## Production
`gunicorn -c backend/gunicorn.conf.py backend.wsgi:app`

## Legacy JSON import
The seed is preserved in `backend/seed_data.json`. If an old installation has `data/ef_database.json`, use the included migration workflow after installing dependencies.

## Checks
`GET /api/health` verifies the Flask application and database configuration.
