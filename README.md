# Mock Transactions API with Support Workflow

![CI](https://github.com/devprofile22/transactions-api/actions/workflows/ci.yml/badge.svg?branch=main)

A small REST API that mimics a payment system, plus the engineering and support process around it: automated tests, a CI/CD pipeline, a Docker image, an uptime monitor, and five production-style incidents handled as ITIL tickets.

## Highlights

| Area | What was built |
|---|---|
| API | Flask REST API: create and fetch transactions, check account balance, health check |
| Database | SQLite with a hand-written schema (primary keys, foreign key, UNIQUE, CHECK) |
| Testing | 13 automated pytest tests, plus a Postman collection with success and failure cases |
| CI/CD | GitHub Actions runs tests on every push; on `main` it builds and pushes the Docker image |
| Containers | Dockerfile, image published on Docker Hub |
| Git workflow | Feature branches and pull requests, no direct work on `main` |
| Monitoring | `monitor.py` pings the API and reports UP/DOWN with an exit code |
| Support process | 5 injected failures, each documented as an ITIL incident ticket and fixed |

## Tech stack

Python 3, Flask, SQLite, pytest, Postman, Docker, GitHub Actions.

## Project structure

```
transactions-api/
├── app.py                  # API code
├── schema.sql              # database schema
├── requirements.txt        # Python dependencies
├── Dockerfile              # container image
├── test_app.py             # pytest tests
├── monitor.py              # uptime monitoring script
├── .github/workflows/ci.yml  # CI/CD pipeline
├── postman/                # Postman collection
├── tickets/                # INC-001 to INC-005 incident tickets
└── docs/                   # screenshots used as evidence
```

## Run it

### Locally

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py
```

The API runs at `http://127.0.0.1:5000`.

### With Docker

```bash
docker run -p 5000:5000 dineshmakhija/transactions-api
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/transaction` | Create a transaction |
| GET | `/transaction/{id}` | Fetch a transaction |
| GET | `/account/{id}` | Fetch an account and its balance |
| GET | `/health` | Health check (also checks the database) |

Example request:

```json
POST /transaction
{
  "reference_id": "TXN-1001",
  "account_id": 1,
  "amount": 500,
  "type": "DEBIT"
}
```

| Status | Meaning |
|---|---|
| 201 | Transaction created |
| 400 | Invalid input (missing field, non-positive amount, bad type) |
| 404 | Account or transaction not found |
| 409 | Duplicate `reference_id` |
| 422 | Insufficient balance |
| 503 | Health check failed (database not reachable) |

## Database schema

Two tables, `accounts` and `transactions`, linked by a foreign key. Integrity rules live in the database as well as in the code: `reference_id` is UNIQUE (stops duplicate payments), `amount` has `CHECK (amount > 0)`, and `balance` has `CHECK (balance >= 0)`. See `schema.sql`.

## Testing

- **pytest:** 13 tests in `test_app.py`. Each test uses its own temporary database, so the real data is never touched. They cover success, bad input, duplicates, missing records, balance changes, response time and the health check.
- **Postman:** a collection with success and failure cases is in `postman/`.

## CI/CD pipeline

```
push  ->  run pytest  ->  (only on main, if tests pass)  ->  build Docker image  ->  push to Docker Hub
```

Pull requests are merged only after the test check is green. Docker Hub credentials are stored as GitHub secrets, never in the code.

## Monitoring

`monitor.py` pings an endpoint and reports UP or DOWN. It exits with code 0 when UP and 1 when DOWN, so other tools can alert on it.

```bash
python monitor.py                                          # check /health once
python monitor.py --watch 10                               # check every 10 seconds
python monitor.py --url http://127.0.0.1:5000/transaction/1  # check any endpoint
```

Results are also appended to `monitor.log`. The screenshot below shows the API going UP, DOWN (container stopped) and UP again:

![Monitoring demo](docs/monitor-demo.png)

## Incident management (ITIL)

Five failures were injected on purpose, one per branch. Each was reproduced, written up as a ticket (issue, impact, steps taken, root cause, resolution, preventive action), fixed through a pull request, and closed. Every ticket includes screenshots as evidence.

| Ticket | Problem | Severity | Priority | How it was detected | Status |
|---|---|---|---|---|---|
| [INC-001](tickets/INC-001.md) | Duplicate transaction processed (UNIQUE constraint missing) | Sev 2 | P2 | pytest and CI failed | Closed |
| [INC-002](tickets/INC-002.md) | Negative amount accepted, balance increased on a DEBIT | Sev 2 | P2 | pytest and CI failed | Closed |
| [INC-003](tickets/INC-003.md) | GET endpoint responds slowly, clients time out | Sev 3 | P3 | monitor.py (tests and CI stayed green) | Closed |
| [INC-004](tickets/INC-004.md) | 500 error instead of 404 for an unknown ID | Sev 3 | P3 | pytest and CI failed | Closed |
| [INC-005](tickets/INC-005.md) | Balance not updated after a successful transaction | Sev 1 | P1 | Reconciliation check (tests and CI stayed green) | Closed |

### SLA matrix used

| Priority | Respond | Resolve |
|---|---|---|
| P1 Critical | 15 min | 1 hr |
| P2 High | 30 min | 4 hrs |
| P3 Medium | 2 hrs | 1 day |
| P4 Low | 1 day | 3 days |

Priority is Impact x Urgency. Severity describes how badly the system is broken technically. INC-005 is Sev 1 / P1 even though the API stayed up, because it silently corrupts money records.

## Key lessons

- **Green tests can hide bugs.** INC-003 and INC-005 passed every test and CI check. Each ticket ended with a new test that fails on the buggy code, so the same bug is caught next time.
- **/health is not enough.** It stayed UP while a real endpoint was broken. Monitor at least one real endpoint.
- **For money logic, test the data, not just the status code.** The balance tests exist because of INC-005.
- **Validate in layers.** Input rules are enforced in both the application and the database.
- **A schema change does not change an existing database file.** After editing `schema.sql`, the database must be recreated or migrated.

## Known limitations

- The Flask development server with `debug=True` is used. This is fine for a learning project but must not be used in production, because debug mode exposes tracebacks.
- `init_db()` re-runs the seed `INSERT` on every start, so extra test accounts can appear. A proper migration or seed step would fix this.
- No authentication, and SQLite is a single-file database.

## What I learned

SQL schema design with constraints, REST API design and status codes, API testing with Postman and pytest, Docker, Git branching and pull requests, CI/CD with GitHub Actions, writing a monitoring script, and writing ITIL-style incident tickets with severity, priority and SLA.