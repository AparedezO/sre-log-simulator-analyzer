# Log Simulator & Analyzer (SRE Practice)

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SRE](https://img.shields.io/badge/SRE-Observability-0A66C2?style=for-the-badge)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Status](https://img.shields.io/badge/Portfolio-Ready-2E7D32?style=for-the-badge)

> A Python project that simulates production-style application logs, analyzes them like an SRE, infers possible root causes, and exposes Prometheus-style metrics.

## Table Of Contents

- [Overview](#overview)
- [What Part Of SRE This Practices](#what-part-of-sre-this-practices)
- [Features](#features)
- [Project Structure](#project-structure)
- [Log Format](#log-format)
- [Setup](#setup)
- [Usage](#usage)
- [Example Analyzer Output](#example-analyzer-output)
- [Metrics Endpoint](#metrics-endpoint)
- [SRE Detection Rules](#sre-detection-rules)
- [Recommended Practice Flow](#recommended-practice-flow)
- [GitHub Readiness](#github-readiness)
- [Future Improvements](#future-improvements)

## Overview

In real production environments, SRE teams spend a lot of time understanding what happened during an incident. Logs are one of the most important observability signals because they describe application behavior in detail.

This project creates a small but realistic SRE practice environment:

- `log_generator.py` simulates logs from an application.
- `log_analyzer.py` reads those logs and identifies operational signals.
- `metrics.py` exposes key values in Prometheus text format through `/metrics`.

The goal is not only to generate text logs. The goal is to practice turning raw operational data into useful incident context.

## What Part Of SRE This Practices

This exercise focuses on the **observability and incident analysis** part of SRE work.

It practices:

- **Log observability:** reading and understanding application events.
- **Signal detection:** identifying errors, slow responses, and failing endpoints.
- **Incident triage:** deciding whether the issue looks like backend failure, database instability, or performance degradation.
- **Metrics extraction:** converting log data into numeric signals that monitoring systems can scrape.
- **Root cause thinking:** using patterns in logs to infer the most likely operational problem.

This is the kind of thinking an SRE uses during an incident:

```text
Raw logs -> Aggregated signals -> Incident hypothesis -> Severity -> Metrics
```

## Features

- Generates logs with realistic timestamps.
- Supports `INFO`, `WARNING`, and `ERROR` log levels.
- Simulates endpoints such as `/login`, `/api/users`, and `/payments`.
- Simulates HTTP status codes such as `200`, `404`, and `500`.
- Adds latency values to every generated request.
- Analyzes logs and counts errors by message.
- Counts HTTP status occurrences.
- Detects most-used endpoints.
- Calculates average latency.
- Calculates error rate.
- Infers root cause and severity.
- Exposes metrics in Prometheus-compatible text format.

## Project Structure

```text
04_log_simulator_analyzer_sre_practice/
├── log_generator.py
├── log_analyzer.py
├── metrics.py
├── requirements.txt
├── README.md
├── .gitignore
└── logs/
    └── .gitkeep
```

## Log Format

Generated logs follow this format:

```text
YYYY-MM-DD HH:MM:SS | LEVEL | MESSAGE | ENDPOINT | HTTP_STATUS | latency=Nms
```

Examples:

```text
2026-01-01 12:00:01 | INFO | Request completed | /api/users | 200 | latency=120ms
2026-01-01 12:00:02 | ERROR | Database connection failed | /payments | 500 | latency=1800ms
2026-01-01 12:00:03 | WARNING | High response time | /login | 200 | latency=1200ms
```

## Setup

This project uses only the Python standard library. No external dependencies are required.

Activate your virtual environment:

```cmd
D:\programacion\08_SRE\venv\Scripts\activate.bat
```

Move into the project:

```cmd
cd /d D:\programacion\08_SRE\04_log_simulator_analyzer_sre_practice
```

Install requirements:

```cmd
pip install -r requirements.txt
```

The `requirements.txt` file is intentionally minimal because the project currently does not need third-party packages.

## Usage

### 1. Generate Logs

Generate 50 logs quickly:

```cmd
python log_generator.py --count 50 --interval 0.2
```

Generate logs continuously:

```cmd
python log_generator.py --loop --interval 1
```

Generate logs into a custom file:

```cmd
python log_generator.py --log-file logs/demo.log --count 100
```

### 2. Analyze Logs

Analyze the default log file:

```cmd
python log_analyzer.py
```

Analyze a custom log file:

```cmd
python log_analyzer.py --log-file logs/demo.log
```

### 3. Start Metrics Server

Start the Prometheus-style metrics endpoint:

```cmd
python metrics.py --port 8001
```

Open this URL in a browser:

```text
http://localhost:8001/metrics
```

Keep the terminal running while using `/metrics`. If the process is stopped, the browser will show `ERR_CONNECTION_REFUSED`.

## Example Analyzer Output

```text
LOG ANALYSIS REPORT
===================
TOTAL LOGS: 50
REQUESTS: 50
ERRORS: 8
WARNINGS: 10
AVERAGE LATENCY: 821.08ms
ERROR RATE: 16.00%

ERRORS:
- Timeout error -> 7
- Database connection failed -> 1

HTTP STATUS:
- 200 -> 29
- 404 -> 13
- 500 -> 8

MOST USED ENDPOINTS:
- /api/users -> 20 requests
- /payments -> 16 requests
- /login -> 14 requests

SRE INFERENCE:
ROOT CAUSE: BACKEND FAILURE
SEVERITY: CRITICAL
```

## Metrics Endpoint

The metrics server exposes values in Prometheus text format.

Example:

```text
# HELP logs_total Total number of logs processed
# TYPE logs_total counter
logs_total 50

# HELP errors_total Total number of error logs
# TYPE errors_total counter
errors_total 8

# HELP requests_total Total number of request logs
# TYPE requests_total counter
requests_total 50

# HELP latency_avg Average observed latency in milliseconds
# TYPE latency_avg gauge
latency_avg 821.08

# HELP error_rate Ratio of errors to requests
# TYPE error_rate gauge
error_rate 0.1600
```

### Metrics Explained

| Metric | Type | Meaning |
|--------|------|---------|
| `logs_total` | Counter | Total log lines processed |
| `errors_total` | Counter | Total `ERROR` log entries |
| `requests_total` | Counter | Total request-like log entries |
| `latency_avg` | Gauge | Average latency in milliseconds |
| `error_rate` | Gauge | Error ratio calculated as `errors_total / requests_total` |

## SRE Detection Rules

The analyzer uses simple rules to infer likely operational issues.

| Signal | Inferred Problem | Severity |
|--------|------------------|----------|
| Many database connection errors | `DATABASE INSTABILITY` | `CRITICAL` |
| Many HTTP `500` responses | `BACKEND FAILURE` | `CRITICAL` |
| High average latency or many slow requests | `PERFORMANCE ISSUE` | `HIGH` |
| Some errors below critical threshold | `APPLICATION ERRORS DETECTED` | `MEDIUM` |
| No meaningful failure pattern | `NO MAJOR INCIDENT DETECTED` | `LOW` |

## Recommended Practice Flow

1. Generate a batch of logs with `log_generator.py`.
2. Run `log_analyzer.py` and read the report.
3. Start `metrics.py` and inspect `/metrics`.
4. Generate more logs and rerun the analyzer.
5. Compare how error rate, latency, status codes, and root cause inference change.

## GitHub Readiness

The project is ready to publish as a portfolio exercise because it includes:

- A clear project purpose.
- Separate generator, analyzer, and metrics modules.
- A clean `.gitignore`.
- A `logs/` folder kept with `.gitkeep`.
- Runtime log files ignored by Git.
- A documented practice flow.
- Example output for interviews and demos.

## Future Improvements

- Add JSON log output.
- Add CSV or JSON analysis reports.
- Add Docker support.
- Add Prometheus scrape configuration.
- Add Grafana dashboard examples.
- Add severity metrics such as `incident_severity{level="critical"} 1`.
- Add unit tests for parsing and inference rules.

## Interview Explanation

You can explain this project like this:

```text
This project simulates production logs, analyzes them for operational signals, infers possible root causes, and exposes metrics in Prometheus format. It practices the observability and incident triage side of SRE work.
```
