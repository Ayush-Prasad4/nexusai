# NexusAI

## Production-Grade Multi-Agent Intelligence & Decision Platform

**NexusAI** is a production-grade multi-agent decision platform that turns complex decision requests into durable, evidence-driven workflows with verification, conflict detection, persistent state, and auditable outputs.

Rather than treating an LLM as a single API call, NexusAI treats AI decision-making as a **distributed backend workflow** with asynchronous execution, multiple specialized agents, durable checkpoints, idempotent processing, failure recovery, security, observability, and automated validation.

---

## Why NexusAI?

Many AI applications stop at:

```text
User → API → LLM → Response
```

NexusAI explores what happens when an AI workflow needs to behave more like a production backend system:

```text
Request
   ↓
Persistent State
   ↓
Async Job Queue
   ↓
Distributed Worker
   ↓
Multi-Agent Workflow
   ↓
Verification & Conflict Detection
   ↓
Decision Synthesis
   ↓
Persistent Result
   ↓
Observable & Recoverable System
```

The project focuses on the engineering challenges around **reliable AI systems**, not just prompt engineering or building another chatbot.

---

## Key Engineering Highlights

* **Multi-agent orchestration** using LangGraph
* **Asynchronous distributed execution** using Redis Streams and dedicated workers
* **Persistent decision state** using PostgreSQL
* **Atomic idempotency** to prevent duplicate decision execution
* **Durable workflow checkpoints** for recovery
* **Retry and failure recovery** with exponential backoff and dead-letter handling
* **JWT authentication and RBAC**
* **Request IDs** for request-level traceability
* **Prometheus + Grafana observability**
* **Dockerized horizontal scaling**
* **Automated unit, integration, security, concurrency, and end-to-end testing**
* **Locust-based performance validation**

---

# Architecture

```text
                         ┌──────────────────┐
                         │      Client      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      Nginx       │
                         │  Reverse Proxy   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌──────────────┐           ┌──────────────┐
             │   FastAPI    │           │   FastAPI    │
             │   API #1     │           │   API #2     │
             └──────┬───────┘           └──────┬───────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌──────────────┐           ┌────────────────┐
             │ PostgreSQL   │           │ Redis Streams  │
             │ Persistent   │           │ Async Job      │
             │ State        │           │ Queue          │
             └──────────────┘           └───────┬────────┘
                                                │
                                      ┌─────────┴─────────┐
                                      ▼                   ▼
                              ┌──────────────┐    ┌──────────────┐
                              │   Worker #1   │    │   Worker #2   │
                              └──────┬───────┘    └──────┬───────┘
                                     │                    │
                                     └─────────┬──────────┘
                                               ▼
                                      ┌────────────────┐
                                      │    LangGraph   │
                                      │ Decision Graph │
                                      └───────┬────────┘
                                              │
                                              ▼
                                      Multi-Agent System
                                              │
                                              ▼
                                      Persisted Decision
```

---

# Decision Workflow

The decision workflow is implemented as a LangGraph state machine:

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

Each stage has a specific responsibility rather than relying on a single general-purpose model call.

### Workflow stages

| Stage              | Responsibility                                   |
| ------------------ | ------------------------------------------------ |
| Research           | Gather and structure relevant information        |
| Verification       | Validate research outputs                        |
| Conflict Detection | Identify inconsistencies or conflicting evidence |
| Analysis           | Produce structured analytical reasoning          |
| Critique           | Challenge and review the analysis                |
| Synthesis          | Produce the final decision and rationale         |

---

# Request Lifecycle

A decision request follows an asynchronous lifecycle:

```text
Client
  │
  ▼
FastAPI
  │
  ▼
Persist PENDING decision
  │
  ▼
Publish Redis job
  │
  ▼
Worker claims job
  │
  ▼
Atomic PENDING/FAILED → RUNNING transition
  │
  ▼
Execute LangGraph
  │
  ├───────────────► FAILED
  │
  ▼
Persist decision + rationale
  │
  ▼
COMPLETED
  │
  ▼
Acknowledge queue message
```

This architecture keeps API request handling separate from potentially expensive AI processing.

---

# Reliability Engineering

NexusAI is designed around the assumption that distributed AI workflows can fail, retry, or be delivered more than once.

## Explicit Lifecycle

Decision runs use explicit persistent states:

```text
PENDING → RUNNING → COMPLETED
                    │
                    └── FAILED
```

This makes workflow state observable and recoverable.

## Atomic Idempotency

Workers do not simply set a run to `RUNNING`.

Instead, the database performs an atomic conditional transition.

Only one worker can successfully claim a given pending/retryable decision:

```text
PENDING ──► RUNNING    Worker A: success
PENDING ──► RUNNING    Worker B: rejected
```

This prevents concurrent duplicate execution.

## Durable Checkpoints

LangGraph checkpoints persist workflow state.

Workers can detect already-completed workflows and avoid executing completed decisions again.

## Retry & Recovery

Redis Streams provides the foundation for durable asynchronous processing.

The worker system supports:

* Consumer groups
* Job claiming
* Heartbeats
* Retry attempts
* Exponential backoff
* Dead-letter handling
* Stale-job recovery
* Explicit message acknowledgement

---

# Security

NexusAI includes application-level security controls suitable for a production-oriented API:

* JWT authentication
* Role-based access control
* Active-user validation
* Configurable request rate limiting
* Request body-size limits
* Host validation
* Configurable CORS
* Request ID generation and propagation
* Structured error handling
* Environment-based secret configuration

Sensitive credentials are supplied through environment variables rather than committed to source control.

---

# Observability

The platform exposes Prometheus metrics for both API and decision-processing behavior.

### HTTP metrics

```text
nexusai_http_requests_total
nexusai_http_request_duration_seconds
```

### Decision-processing metrics

```text
nexusai_decision_jobs_total
nexusai_decision_job_duration_seconds
nexusai_decision_queue_depth
```

The local scaled environment includes:

* Nginx
* 2 API replicas
* 2 worker replicas
* PostgreSQL
* Redis
* Prometheus
* Grafana

This provides visibility into request performance, decision processing, and queue behavior.

---

# Technology Stack

| Area          | Technology     |
| ------------- | -------------- |
| Language      | Python 3.12    |
| API           | FastAPI        |
| AI Workflow   | LangGraph      |
| Database      | PostgreSQL     |
| ORM           | SQLAlchemy     |
| Migrations    | Alembic        |
| Queue         | Redis Streams  |
| Reverse Proxy | Nginx          |
| Containers    | Docker         |
| Metrics       | Prometheus     |
| Dashboards    | Grafana        |
| Testing       | Pytest         |
| Load Testing  | Locust         |
| CI/CD         | GitHub Actions |

---

# Engineering Validation

NexusAI is validated through automated testing and performance testing rather than relying only on a working local demo.

## Automated Testing

The test suite covers:

* API behavior
* Authentication
* JWT security
* RBAC
* Configuration validation
* Error handling
* Request IDs
* Decision lifecycle
* Atomic idempotency
* Concurrent worker claims
* Persistence
* Retry/recovery behavior
* LangGraph workflow execution
* End-to-end decision processing

The current project contains **120+ automated tests**.

### End-to-End Validation

The E2E workflow validates the complete path:

```text
API Request
     ↓
PostgreSQL persistence
     ↓
Redis job queue
     ↓
Decision worker
     ↓
LangGraph workflow
     ↓
PostgreSQL result
     ↓
Queue acknowledgement
```

---

# Load Test Baseline

A Locust baseline was performed against the `/v1/health/live` endpoint through the scaled Docker Compose environment.

## 50 Concurrent Users

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

A separate 10-user baseline completed with:

* 884 requests
* 0 failures
* 29.70 req/s
* P95: 9 ms
* P99: 14 ms

> **Benchmark scope:** these measurements validate the API/infrastructure health path through Nginx and the scaled API deployment. They are **not** a benchmark of the complete LLM-powered decision workflow.

---

# Local Development

## Standard Environment

```bash
docker compose up -d
```

## Scaled Environment

```bash
docker compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

The scaled environment runs:

```text
2 × FastAPI API
2 × Decision Workers
1 × Nginx
1 × PostgreSQL
1 × Redis
1 × Prometheus
1 × Grafana
```

## Run Tests

```bash
pytest -q
```

## Run Load Test

```bash
locust -f tests/load/locustfile.py \
  --headless \
  -u 50 \
  -r 5 \
  -t 60s \
  --host http://localhost:8003
```

---

# Project Structure

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

---

# Engineering Focus

NexusAI focuses on the intersection of **AI engineering, backend engineering, and distributed systems**.

The project demonstrates practical work with:

* Multi-agent orchestration
* Agentic workflows
* Durable state management
* Asynchronous job processing
* Distributed worker coordination
* Idempotent execution
* Failure recovery
* API security
* Observability
* Containerized deployment
* Automated testing
* Performance validation

The goal is not to build another chatbot.

The goal is to demonstrate how an AI-powered decision workflow can be engineered as a **reliable, observable, secure, and recoverable production system**.
