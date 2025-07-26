# Deployment Guide

This project can be deployed using Docker and Docker Compose.

## Build the Image

```bash
docker build -t calendar-app .
```

## Run with Docker Compose

Update `.env` or environment variables as needed. The provided
`docker-compose.yml` starts the API and a PostgreSQL database.

```bash
docker compose up -d
```

The API will be available on `http://localhost:8000`.
