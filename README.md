# NexusAI

NexusAI is a production-grade multi-agent intelligence and decision platform designed to demonstrate how AI decision workflows can be built as reliable backend systems rather than simple LLM wrappers.

## What NexusAI Demonstrates

* Multi-agent decision workflows with LangGraph
* Asynchronous job processing with Redis Streams
* Persistent state and results with PostgreSQL
* Durable workflow checkpoints
* Idempotent worker execution
* Retry and failure recovery
* JWT authentication and RBAC
* Request tracing with request IDs
* Prometheus and Grafana observability
* Dockerized and horizontally scalable services

## Architecture

```text
Client
  │
  ▼
Nginx
  │
  ├───────────────┐
  ▼               ▼
FastAPI #1     FastAPI #2
  │               │
  └───────┬───────┘
          │
     ┌────┴─────┐
     ▼          ▼
PostgreSQL   Redis Streams
                │
                ▼
        ┌─────────────────┐
        │ Decision Workers │
        │     #1 / #2      │
        └────────┬─────────┘
                 │
                 ▼
             LangGraph
                 │
                 ▼
       Multi-Agent Workflow
                 │
                 ▼
       Persisted Decision
```

## Decision Workflow

```text
START
  │
  ▼
Prepare
  │
  ▼
Research
  │
  ▼
Verification
  │
  ▼
Conflict Detection
  │
  ▼
Analysis
  │
  ▼
Critique
  │
  ▼
Synthesis
  │
  ▼
Complete
  │
  ▼
END
```

The workflow uses specialized stages for research, verification, conflict detection, analysis, critique, and final synthesis.

## Request Lifecycle

A decision request follows an asynchronous lifecycle:

```text
API Request
    │
    ▼
Persist PENDING run
    │
    ▼
Publish Redis job
    │
    ▼
Worker claims job
    │
    ▼
Atomically transition to RUNNING
    │
    ▼
Execute LangGraph workflow
    │
    ├──────────────► FAILED
    │
    ▼
Persist decision + rationale
    │
    ▼
COMPLETED
```

This separates request handling from potentially expensive decision processing.

## Reliability Engineering

### Lifecycle Management

Decision runs use explicit states:

```text
PENDING → RUNNING → COMPLETED
                    │
                    └── FAILED
```

State transitions are persisted in PostgreSQL.

### Idempotency

Workers use an atomic database transition when claiming a decision run.

Only one worker can successfully transition a `PENDING` or retryable `FAILED` run to `RUNNING`.

This prevents duplicate workers from concurrently executing the same decision.

### Durable Checkpoints

LangGraph checkpoints persist workflow state. Workers can detect already-completed workflows and avoid re-running completed decisions.

### Retry and Recovery

The Redis Streams worker system supports:

* Consumer groups
* Job claiming
* Heartbeats
* Retry attempts
* Exponential backoff
* Dead-letter handling
* Recovery of stale jobs

### Persistent State

Decision state, results, rationale, and failure information are persisted in PostgreSQL instead of existing only in process memory.

## Technology Stack

| Layer         | Technology    |
| ------------- | ------------- |
| API           | FastAPI       |
| Language      | Python 3.12   |
| Workflow      | LangGraph     |
| Database      | PostgreSQL    |
| ORM           | SQLAlchemy    |
| Migrations    | Alembic       |
| Queue         | Redis Streams |
| Reverse Proxy | Nginx         |
| Containers    | Docker        |
| Metrics       | Prometheus    |
| Dashboards    | Grafana       |
| Testing       | Pytest        |
| Load Testing  | Locust        |

## API and Security

The API is versioned under `/v1`.

Security and backend controls include:

* JWT authentication
* Role-based access control
* Active-user validation
* Request rate limiting
* Request body-size limits
* Configurable CORS
* Host validation
* Request ID generation and propagation
* Structured error handling

Secrets are provided through environment variables rather than committed to the repository.

## Observability

NexusAI exposes Prometheus metrics for API and decision-processing behavior.

Tracked metrics include:

```text
nexusai_http_requests_total
nexusai_http_request_duration_seconds
nexusai_decision_jobs_total
nexusai_decision_job_duration_seconds
nexusai_decision_queue_depth
```

The scaled local environment runs:

* 2 API replicas
* 2 worker replicas
* Nginx
* PostgreSQL
* Redis
* Prometheus
* Grafana

## Load Test Baseline

A Locust baseline was executed against `/v1/health/live` through the scaled Docker Compose environment.

### 50 Concurrent Users

| Metric           |       Result |
| ---------------- | -----------: |
| Concurrent users |           50 |
| Duration         |   60 seconds |
| Requests         |        9,065 |
| Failures         |            0 |
| Failure rate     |           0% |
| Throughput       | 151.56 req/s |
| P50              |         3 ms |
| P95              |         8 ms |
| P99              |        10 ms |
| P99.9            |        39 ms |
| Maximum          |        91 ms |

A separate 10-user baseline completed with 0% failures at approximately 29.7 req/s.

> These measurements benchmark the API/infrastructure health path. They are not a benchmark of the complete LLM-powered decision workflow.

## Testing

The project contains unit, integration, authentication, lifecycle, idempotency, persistence, request-ID, and end-to-end workflow tests.

The end-to-end flow covers:

```text
API
 ↓
PostgreSQL
 ↓
Redis
 ↓
Worker
 ↓
LangGraph
 ↓
PostgreSQL result
 ↓
Queue acknowledgement
```

The current test suite contains more than 120 automated tests.

## Local Development

### Start the standard environment

```bash
docker compose up -d
```

### Start the scaled environment

```bash
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Run tests

```bash
pytest -q
```

### Run the load test

```bash
locust -f tests/load/locustfile.py \
  --headless \
  -u 50 \
  -r 5 \
  -t 60s \
  --host http://localhost:8003
```

## Project Structure

```text
nexusai/
├── app/
│   ├── api/
│   ├── application/
│   │   └── workflows/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   ├── workers/
│   └── main.py
├── migrations/
├── monitoring/
│   ├── grafana/
│   └── prometheus/
├── nginx/
├── tests/
│   ├── auth/
│   ├── integration/
│   ├── load/
│   └── ...
├── docker-compose.yml
├── docker-compose.scale.yml
├── Dockerfile
└── pyproject.toml
```

## Engineering Focus

NexusAI focuses on the engineering challenges around production AI workflows:

* Multi-agent orchestration
* Durable state management
* Asynchronous processing
* Distributed worker coordination
* Idempotent execution
* Failure recovery
* API security
* Observability
* Containerized deployment
* Automated testing
* Performance validation

The project is intentionally focused on building a reliable AI decision system rather than a simple chatbot or single LLM API wrapper.
