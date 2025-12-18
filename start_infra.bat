@echo off
echo Starting Infrastructure Containers...

REM Stop existing containers if they exist
docker stop gst-postgres >nul 2>&1
docker rm gst-postgres >nul 2>&1
docker stop gst-redis >nul 2>&1
docker rm gst-redis >nul 2>&1

REM Start PostgreSQL
docker run ^
  --name gst-postgres ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=password ^
  -e POSTGRES_DB=gst_compliance_db ^
  -p 5432:5432 ^
  -v gst_postgres_data:/var/lib/postgresql/data ^
  --restart unless-stopped ^
  -d postgres:15-alpine

REM Start Redis
docker run ^
  --name gst-redis ^
  -p 6379:6379 ^
  --restart unless-stopped ^
  -d redis:alpine

echo.
echo Containers started successfully!
echo.
echo Postgres: localhost:5432
echo Redis: localhost:6379
echo.
echo You can now run:
echo   uvicorn app.main:app --reload
echo   rq worker
pause
