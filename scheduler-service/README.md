# Desk Scheduler Service

## Features

- Schedule desk movements using cron expressions
- Manual desk control endpoints
- In-memory job storage (no database required)
- Default cleaning mode schedules (8 PM - 9 PM)
- Easy schedule management through code
- RESTful API with automatic documentation

## Project Structure

```
scheduler-service/
├── main.py                 # FastAPI application entry point
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── scheduler.py    # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── scheduler.py    # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── desk_service.py      # Desk API integration
│       └── scheduler_service.py # APScheduler management
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

## Installation

### Using Docker Compose (Recommended)

1. Configure environment variables in `docker-compose.yml`:
   ```yaml
   environment:
     - DESK_API_BASE_URL=http://your-desk-api-url/api/v2
     - DESK_API_KEY=your_api_key_here
     -DESK_API_TIMEOUT_SECONDS=10
   ```

2. Start the service:
   ```bash
   docker-compose up -d
   ```

### Local Development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Followw logs
   ```bash
docker logs -f scheduler-service
   ```

3. Run the service:
   ```bash
   uv run fastapi dev --host 0.0.0.0 --port 8001
   ```

## Managing Schedules

### Managing Schedules via the API

Schedules are now stored in PostgreSQL (`schedule_jobs` table) and mirrored into
APScheduler when the service starts. You can create, update, or delete schedules
through the REST API exposed by the service:

- `POST /scheduler/api/v1/schedules` – create a new schedule.
- `PUT /scheduler/api/v1/schedules/{job_id}` – update an existing schedule.
- `DELETE /scheduler/api/v1/schedules/{job_id}` – remove a schedule.
- `GET /scheduler/api/v1/schedules` – list all schedules along with the next run.

When running locally, `docker-compose.standalone.yml` provisions a PostgreSQL
instance (`scheduler-db`) and seeds default schedules on first startup. The
`/scheduler/api/v1/schedules` endpoint returns the combined database and runtime
state so that the frontend admin console can manage entries.
```

### Schedule Parameters

- **job_id**: Unique identifier for the schedule (string)
- **name**: Human-readable name for the schedule
- **action**: Either `'raise'` or `'lower'`
- **position_mm**: Target position in millimeters (0-1200)
- **hour**: Hour (0-23)
- **minute**: Minute (0-59)
- **day_of_week**: Days to run the schedule:
  - `'*'` - Every day
  - `'mon-fri'` - Weekdays only
  - `'mon,wed,fri'` - Specific days
  - `'0-6'` - Days by number (0=Monday, 6=Sunday)

### Managing Schedules via API

You can also add, modify, and delete schedules at runtime using the API:

#### Create a Schedule
```bash
curl -X POST "http://localhost:8001/api/v1/schedules" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Morning standup",
    "action": "raise",
    "position_mm": 1100,
    "cron": {
      "hour": 9,
      "minute": 0,
      "day_of_week": "mon-fri"
    }
  }'
```

#### List All Schedules
```bash
curl "http://localhost:8001/api/v1/schedules"
```

#### Delete a Schedule
```bash
curl -X DELETE "http://localhost:8001/api/v1/schedules/morning_standup"
```

## API Endpoints

### Health Check
```
GET /api/v1/health
curl -s http://127.0.0.1:8001/api/v1/health
```

### Manual Desk Control
```
POST /api/v1/desks/manual/raise    # Raise all desks
POST /api/v1/desks/manual/lower    # Lower all desks
GET  /api/v1/desks                 # Retrieve all desk status

curl -s -X POST http://127.0.0.1:8001/api/v1/desks/manual/raise -H "Content-Type: application/json" -d "{\"position_mm\":1100}"
curl -s -X POST http://127.0.0.1:8001/api/v1/desks/manual/lower -H "Content-Type: application/json" -d "{\"position_mm\":680}"

```

## Example Requests

### Manual Desk Control
```bash
curl -X POST "http://localhost:8001/api/v1/desks/manual/raise" \
  -H "Content-Type: application/json" \
  -d '{"position_mm": 1200}'
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8001/docs
http://127.0.0.1:8001/docs

## Default Schedules

The service automatically creates two default schedules:
- **Cleaning Start** (20:00 daily): Raises all desks to 1200mm
- **Cleaning End** (21:00 daily): Lowers all desks to 680mm

