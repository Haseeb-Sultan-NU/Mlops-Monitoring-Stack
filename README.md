# MLOps Monitoring Stack — Prometheus + Grafana

![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

A production-ready monitoring and alerting stack for ML systems — combining **Prometheus**, **Alertmanager**, and **Grafana** with a custom Python exporter, pre-built dashboards, and Kubernetes manifests for real-time observability of model performance and infrastructure health.

---

## 🚀 Quickstart (Docker Compose)

```bash
git clone https://github.com/your-username/monitoring-stack.git
cd monitoring-stack
docker-compose up -d
```

| Service | URL | Credentials |
|---------|-----|-------------|
| **Prometheus** | http://localhost:9090 | — |
| **Grafana** | http://localhost:3000 | `admin / admin` |
| **Alertmanager** | http://localhost:9093 | — |

---

## 🏗️ Stack Architecture

```
ML Application / Services
        │
        ▼
Python Exporter
(custom /metrics endpoint)
        │
        ▼
Prometheus
(scraping, rules, storage)
        │
        ├──────────────────┐
        ▼                  ▼
Alertmanager           Grafana
(threshold alerts,     (dashboards,
 webhook routing)       visualization)
```

---

## 🔍 What Gets Monitored

| Metric Type | Examples |
|:---|:---|
| **Throughput** | Requests per second (RPS) |
| **Latency** | Inference response time (p50, p95, p99) |
| **Error Rate** | 5xx response percentage |
| **Saturation** | CPU, memory, pod utilization |
| **Alerting** | Threshold breaches → Alertmanager → webhooks |

---

## 🚀 Key Features

**Custom Python Exporter**
Lightweight Python application exposing domain-specific Prometheus metrics via a `/metrics` endpoint — drop-in compatible with any ML inference service.

**Pre-built Grafana Dashboards**
Provisioned dashboards for immediate visibility into request rate, latency distributions, and system health — no manual setup required.

**Alertmanager Integration**
Configurable alerting rules with routing to webhooks, Slack, or email on SLA breaches (latency spikes, elevated error rates, resource saturation).

**Kubernetes-Ready**
Includes K8s manifests for deploying the full stack to a cluster alongside your ML workloads.

**Load Testing Scripts**
Helper scripts for simulating traffic and validating alert thresholds before production deployment.

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Metrics Collection** | Prometheus |
| **Alerting** | Alertmanager |
| **Visualization** | Grafana |
| **Custom Exporter** | Python |
| **Local Deployment** | Docker Compose |
| **Cluster Deployment** | Kubernetes |

---

## 📂 Repository Structure

```
monitoring-stack/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
├── alertmanager/
│   └── alertmanager.yml
├── grafana/
│   ├── provisioning/
│   └── dashboards/
├── app/
│   └── python-exporter/
├── k8s/
└── scripts/
```

| Path | Description |
|------|-------------|
| `docker-compose.yml` | Full local stack — one command startup |
| `prometheus/` | Scrape config and alerting rules |
| `alertmanager/` | Alert routing and notification config |
| `grafana/` | Auto-provisioned dashboards |
| `app/python-exporter/` | Custom metrics exporter |
| `k8s/` | Kubernetes manifests |
| `scripts/` | Load testing and automation helpers |

---

## ☸️ Kubernetes Deployment

```bash
kubectl apply -f k8s/
```

---
