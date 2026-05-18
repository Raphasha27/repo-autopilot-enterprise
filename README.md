# 🚀 Repo Autopilot Enterprise

An Enterprise AI DevOps & GitOps Orchestration Platform designed to manage, analyze, and autonomously heal multiple Git repositories.

## 🏗️ Architecture

This repository contains the full production-ready system blueprint:
- **Control Plane (`/control-plane`)**: FastAPI backend orchestrating GitHub webhooks, AI decisions, and Redis queues.
- **Workers (`/workers`)**: Kubernetes-ready Python workers for static analysis, automated CI fixes, PR generation, and safe Git execution.
- **Data & Policy Layer**: Database schemas (`/db/schema.sql`) for strict audit logging, and a Policy Engine for blocking risky AI operations.
- **Frontend Dashboard (`/frontend/dashboard`)**: A gorgeous, high-fidelity React + Vite frontend featuring real-time interactive telemetry charts, glassmorphism design, and AI audit logs.
- **Infrastructure (`/k8s`, `/infra`, `/github-actions`)**: Complete setup including Prometheus monitoring, Grafana dashboards, Helm values, and K8s deployments.

## 🛡️ Security & Governance
This platform enforces strict governance rules:
- No automatic merges without CI success.
- Direct blocking of destructive Git commands (e.g., branch deletions).
- No pushing to production infrastructure without manual operator approval.

## 🚀 Running Locally

### 1. Start the React UI Dashboard
```bash
cd frontend/dashboard
npm install
npm run dev
```
Navigate to `http://localhost:5173/` to view the local simulation.

### 2. (Optional) Run the Control Plane API
```bash
cd control-plane
pip install fastapi uvicorn pydantic requests
uvicorn main:app --reload --port 8000
```
