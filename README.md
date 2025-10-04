### Cloud Native Infra Simulation – Full DevOps Stack in Action

A single-source-of-truth playbook to build, observe, secure, and operate a cloud‑native system using FastAPI + Traefik + Docker Compose (later k3d/Kubernetes), with OpenTelemetry, Prometheus/Grafana/Loki/Tempo, GitHub Actions + GHCR, Terraform, and Cloudflare. Follow this README from Day 0 to production and beyond.

---

### TL;DR (Stack and Principles)
- **App**: FastAPI (Python) + PostgreSQL + Redis
- **Ingress/Proxy**: Traefik (automatic routing, TLS, metrics)
- **Runtime**: Docker Compose → k3d/k3s (later)
- **Observability**: OpenTelemetry SDK + Collector; Prometheus (metrics), Loki (logs), Tempo (traces), Grafana (dashboards), Alertmanager (alerts)
- **CI/CD**: GitHub Actions → GHCR (multi-arch images, scans) → deploy
- **IaC**: Terraform (Cloud: compute/VPC/DNS), Cloudflare (DNS/SSL)
- **Security**: Least privilege, image scanning, SOPS (optional) for encrypted config, secrets in CI environments
- **Reliability**: Health checks, readiness/liveness, automated backups and restore drills

Guiding principles: start simple, instrument from Day 1, automate repeatables, secure by default, document decisions.

---

### Table of Contents
- Why this project
- Architecture overview
- Repository layout
- Environments and prerequisites
- Phase roadmap (acceptance criteria + commands)
- Local development with Docker Compose
- Observability (OTel, Prom, Grafana, Loki, Tempo, Alertmanager)
- CI/CD with GitHub Actions and GHCR
- Terraform and Cloudflare (IaC and DNS/SSL)
- Security hardening checklist
- SLO/SLI and alerting baseline
- Backups and disaster recovery
- Migrating to k3d/Kubernetes
- Demos and documentation assets
- Runbooks (incident and change)
- Appendix (commands/reference)

---

### Why this project
Build a demonstrable, observable, and secure cloud‑native system that showcases DevOps/SRE/Cloud/Backend fundamentals, with clear progression from Docker Compose to Kubernetes. Each phase ends with visible artifacts (dashboards, alerts, deployment screenshots) suitable for a portfolio.

---

### Architecture overview

```mermaid
flowchart LR
  subgraph Client
    Browser
  end

  subgraph Edge/CDN
    CF[Cloudflare DNS/SSL]
  end

  subgraph Ingress
    Traefik[Traefik Reverse Proxy]
  end

  subgraph App
    FE[Frontend (optional React SPA)]
    API[FastAPI Service]
    Worker[Background Worker (Celery/RQ optional)]
  end

  subgraph Data
    PG[(PostgreSQL)]
    Redis[(Redis)]
  end

  subgraph Observability
    OTel[OpenTelemetry Collector]
    Prom[Prometheus]
    Graf[Grafana]
    Loki[(Loki)]
    Tempo[(Tempo)]
    Alert[Alertmanager]
  end

  Browser --> CF --> Traefik
  Traefik --> FE
  Traefik --> API
  API --> PG
  API --> Redis
  Worker --> Redis
  API --> OTel
  Worker --> OTel
  OTel --> Prom
  OTel --> Loki
  OTel --> Tempo
  Prom --> Alert
  Graf --> Prom
  Graf --> Loki
  Graf --> Tempo
```

Key decisions:
- Traefik terminates TLS (later Full/Strict TLS via Cloudflare).
- OpenTelemetry used for traces/metrics/logs export. Centralized collectors fan out to Prom/Loki/Tempo.
- Minimal RBAC/secrets exposure; prefer environment‑scoped secrets.

---

### Repository layout (monorepo)

```
Cloud/
├─ apps/
│  ├─ api/                 # FastAPI service (instrumented)
│  ├─ worker/              # Optional async worker (Celery/RQ)
│  └─ frontend/            # Optional React SPA
├─ deploy/
│  ├─ compose/             # Docker Compose stack for local/cloud VM
│  └─ k8s/                 # Manifests/Helm for k3d/K8s (later)
├─ infra/
│  └─ terraform/           # Cloud infra modules (network/compute/dns)
├─ observability/
│  ├─ grafana/             # Dashboards JSON + provisioning
│  ├─ prometheus/          # Prometheus config + alert rules
│  ├─ loki/                # Loki config
│  ├─ tempo/               # Tempo config
│  └─ otel-collector/      # Collector pipelines
├─ .github/workflows/      # GitHub Actions pipelines
└─ docs/                   # Diagrams, runbooks, ADRs, screenshots
```

Create empty directories to start; fill as phases progress.

---

### Environments and prerequisites

Required locally:
- Windows 10/11 with WSL2 enabled
- Docker Desktop (with WSL2 backend)
- Git, Python 3.11+
- Optional: `just` or Make (task runner). Windows-friendly PowerShell scripts are fine.

Cloud/services:
- Cloudflare account (domain + DNS)
- GitHub (Actions + GHCR)
- Optional: Oracle Cloud Always Free / AWS Free Tier / GCP Free Tier

Environment files:
- `apps/api/.env.example` → copy to `.env`
- `deploy/compose/.env.example` → copy to `.env`
- Never commit real secrets; use GitHub Environments secrets for CI/CD.

---

### Phase roadmap (acceptance criteria + what to do next)

#### Phase 1 (Week 1–2): Local baseline with Compose
Goals:
- FastAPI + PostgreSQL + Redis + Traefik running locally via Compose
- Health endpoints: `/healthz`, `/readyz`, `/livez`
- Basic OpenTelemetry instrumentation; metrics visible in Grafana

Acceptance criteria:
- `docker compose up -d` brings up all services; `http(s)://local.test` (or localhost) responds
- Grafana shows API latency p95, error rate, Postgres/Redis metrics
- Logs flow to Loki; traces visible in Tempo via Grafana explore

Commands (indicative):
```bash
cd deploy/compose
cp .env.example .env
docker compose pull
docker compose up -d
docker compose ps
```

Artifacts to produce:
- Screenshots: Grafana dashboards; service topology; `docker compose ps`
- Commit: initial Compose files, basic FastAPI app, OTel config

#### Phase 2 (Week 3–4): IaC and cloud footprint
Goals:
- Terraform creates network, compute (VM), security groups, and Cloudflare DNS records
- Optional: Cloud VM runs the same Compose stack with outbound‑only access for data plane where possible

Acceptance criteria:
- `terraform plan/apply` completes with remote state configured
- Cloudflare DNS resolves domain to VM; only 80/443/22 exposed
- HTTPS served via Cloudflare (Full/Strict if possible)

Artifacts:
- Terraform modules for `network`, `compute`, `dns`
- Screenshots: Terraform apply summary; Cloudflare DNS panel

#### Phase 3 (Week 4–5): CI/CD → GHCR → deployment
Goals:
- GitHub Actions: lint/test → secure build (multi‑arch) → scan (Trivy) → push to GHCR → deploy (manual approval)

Acceptance criteria:
- PR builds pass; on merge to `main`, images are tagged and available in GHCR
- A controlled job updates the remote stack (SSH/Ansible/scripted) with zero/minimal downtime

Artifacts:
- `.github/workflows/*.yml` pipelines
- Screenshots: Actions runs; GHCR package versions

#### Phase 4 (Week 6–7): Observability and alerting
Goals:
- Prometheus rules + Alertmanager routes (email/Telegram)
- Dashboards: API latency/throughput/errors; infra; blackbox checks

Acceptance criteria:
- Fault injection (e.g., CPU spike, error burst) triggers alerts
- Operators can navigate logs ↔ metrics ↔ traces in Grafana

Artifacts:
- Alert rules/routing; dashboards JSON; screenshots of alerts and dashboards

#### Phase 5 (Week 8–9): Elasticity and self‑healing (k3d/K8s)
Goals:
- k3d local cluster; manifests/Helm for app + observability; HPA (CPU/QPS/custom)
- Optional: KEDA for Redis queue length scaling

Acceptance criteria:
- Load test triggers horizontal scaling; pods recover from failures automatically

Artifacts:
- Manifests/Helm charts; screenshots of scaling events

#### Phase 6 (Week 10): Security hardening and final docs
Goals:
- TLS everywhere, minimal ports, SSH key‑only, image/user hardening, backups and restore drills, runbooks

Acceptance criteria:
- No high‑severity findings in scans; successful DB restore drill; finalized docs with diagrams and screenshots

---

### Local development with Docker Compose

Structure (indicative):
```
deploy/compose/
  docker-compose.yml
  traefik/
    traefik.yml
    dynamic/
      routers.yml
  prometheus/
    prometheus.yml
    alerts.yml
  grafana/
    provisioning/
      dashboards/
      datasources/
  loki/
    loki-config.yml
  tempo/
    tempo-config.yml
  otel-collector/
    config.yaml
  .env.example
```

Traefik basics:
- EntryPoints `:80` and `:443`; routers by host rules; middleware for redirect/http to https
- Attach labels to services (API, frontend) for routing and TLS certs (Cloudflare DNS/TLS handled at edge; local dev can be HTTP or mkcert)

FastAPI basics:
- Include `/healthz`, `/readyz`, `/livez`
- Instrument with `opentelemetry-instrument` or explicit SDK setup

Example dev loop:
```bash
docker compose up -d --build
docker compose logs -f api
docker compose exec api pytest -q
```

---

### Observability

OpenTelemetry Collector (indicative pipelines):
```yaml
receivers:
  otlp:
    protocols:
      http:
      grpc:
exporters:
  prometheus:
    endpoint: ":8889"
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  otlp/tempo:
    endpoint: http://tempo:4317
    tls:
      insecure: true
processors:
  batch: {}
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo]
```

Prometheus targets:
- Traefik metrics endpoint
- OTel Collector `:8889`
- cAdvisor + node‑exporter (container and host metrics)
- Postgres exporter, Redis exporter
- Blackbox exporter (HTTP endpoints and DNS)

Grafana:
- Pre‑provision datasources: Prometheus, Loki, Tempo
- Import or version dashboards in `observability/grafana/`

Alertmanager:
- Configure routes for email/Telegram; silence windows during deployments

---

### CI/CD with GitHub Actions and GHCR

Pipeline stages (PR → main):
1) Lint and unit tests
2) Build multi‑arch images (amd64/arm64) with Buildx
3) Security scans: Trivy (images), Semgrep/tfsec (code/IaC)
4) Push to GHCR with semantic tags (`:commit`, `:branch`, `:vX.Y.Z`)
5) Deploy job (manual approval) to remote (SSH/Ansible/script)

Required secrets/vars (GitHub Environments):
- `GHCR_TOKEN` (or use GITHUB_TOKEN for GHCR)
- `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_KEY`
- Optional cloud credentials via OIDC (recommended) or short‑lived tokens

Versioning:
- Tag releases; embed git SHA and build date as labels and `/version` endpoint

Rollback:
- Keep last known good tag; rollback script updates Compose to pinned image tags

---

### Terraform and Cloudflare

Terraform layout:
```
infra/terraform/
  modules/
    network/
    compute/
    dns/
  envs/
    dev/
      main.tf
      variables.tf
      backend.tf
      outputs.tf
```

Recommendations:
- Use remote state with locking (Terraform Cloud free or object storage)
- Prefer GitHub OIDC to cloud providers to avoid long‑lived keys
- Cloudflare provider for DNS records; set proxied A/AAAA; SSL mode Full (Strict)

Apply (indicative):
```bash
cd infra/terraform/envs/dev
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

Post‑provision:
- Configure the VM with Docker + Compose (cloud‑init/Ansible)
- Pull environment from GitHub Environments → deploy latest images

---

### Security hardening checklist
- Run containers as non‑root; set explicit `USER` and fs permissions
- Minimal exposed ports; only `80/443/22` inbound; restrict SSH by IP if possible
- Health/readiness probes; Traefik middlewares (rate‑limit, headers, redirect to HTTPS)
- Regular dependency and image scanning (Trivy in CI)
- Secrets: environment‑scoped via GitHub Environments; optional SOPS + age for at‑rest encryption
- DB: strong passwords, TLS when applicable, least privileges, rotate credentials
- Logging: avoid sensitive data; structured logs; retention policies
- Backups encrypted; test restore regularly

---

### SLO/SLI and alerting baseline
- Availability: API ≥ 99.0% over 30 days
- Latency: API p95 < 300 ms
- Error budget: 5xx rate < 1%

Indicative alerts (PromQL snippets):
```
# High error rate (rolling 5m)
sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m]))
  / sum(rate(http_server_requests_seconds_count[5m])) > 0.01

# High latency p95 (over 5m)
histogram_quantile(0.95, sum(rate(http_server_request_duration_seconds_bucket[5m])) by (le)) > 0.3

# Instance down
up == 0
```

Route alerts via Alertmanager to email/Telegram; add maintenance silence during deploys.

---

### Backups and disaster recovery
- PostgreSQL: use WAL‑G or pgBackRest to object storage (daily full + continuous WAL)
- Redis: RDB snapshots as needed (if used for persistence)
- Test restore quarterly (document steps and timing)
- Keep infra state (Terraform) backed up and locked; version dashboards/configs in git

---

### Migrating to k3d/Kubernetes (Phase 5)
- Stand up k3d locally; convert services to manifests/Helm
- Traefik as IngressController; reuse TLS and routing rules
- OpenTelemetry Collector as DaemonSet/Deployment; use Operator optionally
- HPA based on CPU + custom metrics (via OTel/Prom Adapter)
- KEDA for queue length (Redis Streams) scaling
- PodDisruptionBudget, anti‑affinity, priority classes
- PVCs for Postgres (or managed DB in cloud)

---

### Demos and documentation assets
- Diagrams (Mermaid in README and draw.io in `docs/`)
- Screenshots: Actions, Grafana, alerts, topology
- Short videos/GIFs: fault injection, auto‑scaling, rollout/rollback
- ADRs (Architecture Decision Records) for major choices and tradeoffs

---

### Runbooks

Incident: elevated 5xx
1) Check Grafana dashboard (errors, latency, saturation)
2) Inspect logs in Loki for recent error bursts
3) Correlate traces in Tempo to find hot paths
4) Roll back to last known good image if regression; open incident ticket and timeline

Change: safe deployment
1) Merge to `main` → build/scan/push
2) Approve deploy job
3) Watch health, logs, and key SLOs; be ready to rollback

---

### Appendix: initial command snippets

Local bootstrap:
```bash
git clone <your-repo>
cd Cloud
mkdir -p apps/api apps/worker apps/frontend deploy/compose observability {observability/grafana,observability/prometheus,observability/loki,observability/tempo,observability/otel-collector} infra/terraform .github/workflows docs
```

Run stack:
```bash
cd deploy/compose
cp .env.example .env
docker compose up -d
```

Build/publish image (example):
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/<org>/api:dev --push apps/api
```

Terraform (dev env):
```bash
cd infra/terraform/envs/dev
terraform init && terraform plan && terraform apply
```

---

### Next step (you are here)
1) Scaffold directories as per repo layout
2) Author minimal FastAPI service with health endpoints
3) Create `deploy/compose/docker-compose.yml` with Traefik, API, PG, Redis
4) Add OpenTelemetry Collector + Prom + Grafana + Loki + Tempo to Compose
5) Commit and bring stack up; capture first dashboards/screenshots

This README remains the single source of truth. Update it as you make decisions, add diagrams/screenshots, and promote phases.


