FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY . .
RUN python -m compileall backend
EXPOSE 5000
CMD ["gunicorn","-c","backend/gunicorn.conf.py","backend.wsgi:app"]
