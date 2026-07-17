import time
import random
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from policy_engine import PolicyEngine, GovernanceRuleResult
from ai_engine import AIEngine, AnalysisReport, CodeFixProposal, PullRequestReview
from scheduler import TaskScheduler, JobQueueItem

app = FastAPI(
    title="Repo Autopilot Enterprise Control Plane",
    description="AI-driven DevOps, GitOps, and repository governance system.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
policy_engine = PolicyEngine(max_prs_per_hour=8)
ai_engine = AIEngine()
scheduler = TaskScheduler()

# In-memory storage for repositories and audit logs
repositories: List[Dict[str, Any]] = []
audit_logs: List[Dict[str, Any]] = []

# Populate 50+ Enterprise Mock Repositories
def populate_repositories():
    services = [
        "auth-service", "payment-mesh", "dispatch-mesh", "ui-core", "supply-intelligence",
        "data-warehouse", "ci-builder", "docker-registry", "k8s-operator", "audit-ledger",
        "pricing-engine", "notification-center", "geospatial-index", "analytics-pipeline",
        "search-indexer", "recommendation-api", "user-profile-db", "billing-coordinator",
        "cart-orchestrator", "inventory-tracker", "shipping-gateway", "metrics-collector",
        "logger-daemon", "config-server", "gateway-proxy", "cache-cluster", "email-worker",
        "sms-gateway", "identity-provider", "permission-manager", "secrets-vault", "backup-daemon",
        "db-migrator", "media-processor", "pdf-generator", "report-scheduler", "websocket-hub",
        "chat-backend", "support-ticketer", "crm-connector", "marketing-tracker", "ab-tester",
        "feature-flagger", "fraud-detector", "risk-analyzer", "compliance-auditor", "translation-service",
        "geolocation-api", "weather-fetcher", "map-renderer", "directions-engine", "distance-calculator"
    ]
    
    owners = ["devops-team", "core-platform", "supplywave-corp", "product-logistics", "security-group"]
    branches = ["main", "develop", "prod"]
    
    for i, name in enumerate(services):
        # Stagger health scores
        if i % 11 == 0:
            health = round(random.uniform(45.0, 68.0), 2)  # Low health
        elif i % 5 == 0:
            health = round(random.uniform(70.0, 85.0), 2)  # Medium health
        else:
            health = round(random.uniform(88.0, 99.5), 2)  # High health
            
        repo_id = f"repo-{1000 + i}"
        repositories.append({
            "id": repo_id,
            "name": name,
            "url": f"https://github.com/supplywave-corp/{name}.git",
            "owner": random.choice(owners),
            "default_branch": random.choice(branches),
            "health_score": health,
            "is_active": True,
            "last_analyzed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - random.randint(100, 36000)))
        })

populate_repositories()

# Populate audit logs with high-fidelity records
def populate_audit_logs():
    now = time.time()
    reasons = [
        "Identified deprecated docker-compose syntax. Code rewritten into pure K8s configuration.",
        "Detected circular imports in dispatch mesh utils. Refactored into a clear layered import tree.",
        "Discovered raw SQL injection vulnerability in search-indexer. Applied parameterized query fix.",
        "Blocked attempt to push configuration file containing private deployment keys.",
        "Triggered auto-fix on payment-mesh following lint errors on pipeline checkout."
    ]
    diffs = [
        "--- compose.yml\n+++ k8s/deployment.yml\n- version: '3'\n- services:\n+ apiVersion: apps/v1\n+ kind: Deployment",
        "--- utils.py\n+++ utils.py\n- from .main import app\n+ # Moved app context import inside function execution layer",
        "--- db.py\n+++ db.py\n- query = f\"SELECT * FROM items WHERE id = '{item_id}'\"\n+ query = \"SELECT * FROM items WHERE id = %s\"",
        "--- config.env\n+++ config.env\n- SECRET_KEY=db_super_password_123\n+ # SECRETS LOADED VIA K8S VAULT SECRET ENVIRONMENT VARIABLES",
        "--- linter.py\n+++ linter.py\n- def run(x,y):\n+ def run(x: int, y: int) -> bool:"
    ]
    types = ["infrastructure-upgrade", "refactoring", "security-hotfix", "governance-block", "ci-auto-heal"]
    
    for i in range(5):
        audit_logs.append({
            "id": f"audit-{2000 + i}",
            "repository_name": repositories[i]["name"],
            "decision_type": types[i],
            "input_prompt": f"Analyze repository {repositories[i]['name']} and address key warnings.",
            "ai_reasoning": reasons[i],
            "proposed_diff": diffs[i],
            "governance_passed": i != 3,  # Banned secrets push failed governance
            "governance_message": "Blocked attempt to write secrets direct to disk" if i == 3 else "Passed safety inspection.",
            "user_approved": i in [0, 2],
            "action_taken": "PR_OPENED" if i in [0, 2] else ("BLOCKED" if i == 3 else "HEALED_BRANCH"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - (i * 7200)))
        })

populate_audit_logs()

# Request Models
class WebhookPayload(BaseModel):
    repository: Dict[str, Any]
    event_type: str  # 'push', 'pull_request', 'workflow_run'
    ref: Optional[str] = None
    pr_details: Optional[Dict[str, Any]] = None
    ci_status: Optional[str] = None

class JobTriggerRequest(BaseModel):
    repository_id: str
    job_type: str
    payload: Dict[str, Any]

class ApprovalRequest(BaseModel):
    audit_log_id: str
    approved: bool
    operator_name: str

# ----------------- FastAPI Endpoints -----------------

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    """
    Retrieves global overview scores, queue metrics, and throughput.
    """
    total_repos = len(repositories)
    avg_health = round(sum(r["health_score"] for r in repositories) / total_repos, 2)
    healthy_count = sum(1 for r in repositories if r["health_score"] >= 80.0)
    warning_count = sum(1 for r in repositories if 60.0 <= r["health_score"] < 80.0)
    critical_count = sum(1 for r in repositories if r["health_score"] < 60.0)
    
    q_stats = scheduler.get_queue_stats()
    
    return {
        "total_repositories": total_repos,
        "average_health_score": avg_health,
        "healthy_repositories": healthy_count,
        "warning_repositories": warning_count,
        "critical_repositories": critical_count,
        "queue_stats": q_stats,
        "recent_alerts": [
            {"repo": "payment-mesh", "msg": "CI failing on merge-candidate, running ci-fixer", "severity": "error"},
            {"repo": "secrets-vault", "msg": "Banned config keys caught in git hook, action blocked", "severity": "warning"},
            {"repo": "supply-intelligence", "msg": "AI PR generated: updated dependency vulnerabilities", "severity": "info"}
        ]
    }

@app.get("/api/repositories")
def get_repositories(search: Optional[str] = None):
    """
    Returns lists of tracked enterprise repositories.
    """
    if search:
        return [r for r in repositories if search.lower() in r["name"].lower()]
    return repositories

@app.get("/api/audit-logs")
def get_audit_logs():
    """
    Returns lists of AI decision logs for auditable compliance checks.
    """
    return audit_logs

@app.post("/api/jobs/trigger")
def trigger_manual_job(req: JobTriggerRequest, background_tasks: BackgroundTasks):
    """
    Manually pushes repository evaluation jobs into the Redis/memory queue.
    """
    repo = next((r for r in repositories if r["id"] == req.repository_id), None)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Check rate limit policy
    recent_jobs = sum(1 for j in scheduler.history if j.repository_id == req.repository_id and time.time() - j.enqueued_at < 3600)
    rate_check = policy_engine.evaluate_rate_limit(recent_jobs)
    if not rate_check.passed:
        raise HTTPException(status_code=429, detail=rate_check.message)
        
    job_id = scheduler.enqueue_job(req.repository_id, req.job_type, req.payload)
    
    # Process job asynchronously in background (simulating worker pods)
    background_tasks.add_task(run_worker_simulation, job_id, repo, req.job_type, req.payload)
    
    return {"status": "queued", "job_id": job_id, "message": f"Job {req.job_type} queued for repository {repo['name']}."}

@app.post("/api/audit-logs/approve")
def approve_ai_decision(req: ApprovalRequest):
    """
    Approve/Reject generated code patches or git updates before execution.
    """
    log = next((l for l in audit_logs if l["id"] == req.audit_log_id), None)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
        
    log["user_approved"] = req.approved
    log["approved_by"] = req.operator_name
    log["action_taken"] = "PR_MERGED" if req.approved else "DISCARDED"
    
    return {"status": "updated", "action": log["action_taken"]}

@app.post("/webhooks/github")
def github_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    GitHub Event API receiving payload hooks from actions.
    """
    repo_name = payload.repository.get("name", "unknown")
    repo = next((r for r in repositories if r["name"] == repo_name), None)
    if not repo:
        # Register on fly
        repo_id = f"repo-{1000 + len(repositories)}"
        repo = {
            "id": repo_id,
            "name": repo_name,
            "url": payload.repository.get("clone_url", f"https://github.com/supplywave-corp/{repo_name}.git"),
            "owner": payload.repository.get("owner", {}).get("login", "devops-team"),
            "default_branch": payload.ref.replace("refs/heads/", "") if payload.ref else "main",
            "health_score": 90.0,
            "is_active": True,
            "last_analyzed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        repositories.append(repo)

    job_type = ""
    if payload.event_type == "push":
        job_type = "repo-analyzer"
    elif payload.event_type == "pull_request":
        job_type = "pr-generator"
    elif payload.event_type == "workflow_run" and payload.ci_status == "failure":
        job_type = "ci-fixer"

    if job_type:
        job_id = scheduler.enqueue_job(repo["id"], job_type, {"payload": payload.dict()})
        background_tasks.add_task(run_worker_simulation, job_id, repo, job_type, {})
        return {"status": "enqueued", "job_id": job_id}
        
    return {"status": "ignored"}

# ----------------- Worker Simulator -----------------

def run_worker_simulation(job_id: str, repo: dict, job_type: str, payload: dict):
    """
    Simulates a background K8s worker container polling a job, communicating with
    AIEngine & PolicyEngine, and writing to audit logs.
    """
    scheduler.poll_job(job_type, f"worker-{job_type}-sim")
    time.sleep(2.5)  # Simulate execution workload time
    
    result = {}
    governance_passed = True
    governance_message = "Passed safety checks."
    diff = None
    reasoning = ""
    
    if job_type == "repo-analyzer":
        # Simulate scanning files
        files_mock = [
            {"name": "main.py", "lines": random.randint(80, 500)},
            {"name": "utils.py", "lines": random.randint(30, 200)},
            {"name": "Dockerfile", "lines": random.randint(10, 40)}
        ]
        report: AnalysisReport = ai_engine.analyze_repository_health(repo["name"], files_mock)
        
        # Update repo scores
        repo["health_score"] = report.health_score
        repo["last_analyzed"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        result = {
            "health_score": report.health_score,
            "architecture_score": report.architecture_score,
            "detected_risks_count": len(report.detected_risks)
        }
        reasoning = f"Heuristics review: overall score resolved to {report.health_score}."
        
    elif job_type == "pr-generator" or job_type == "ci-fixer":
        # Generate code fix
        bug = "Resolved CI tests failure / typing standard enforcement"
        fix: CodeFixProposal = ai_engine.generate_code_fix(repo["name"], bug, "main.py", "")
        
        # Policy Engine validation check
        policy_check: GovernanceRuleResult = policy_engine.evaluate_proposed_code(fix.proposed_diff, "main.py")
        governance_passed = policy_check.passed
        governance_message = policy_check.message
        
        diff = fix.proposed_diff
        reasoning = fix.explanation
        
        result = {
            "risk_level": fix.risk_level,
            "governance_passed": governance_passed,
            "applied_patches": 1
        }
        
    # Append execution into permanent audit ledger
    audit_logs.insert(0, {
        "id": f"audit-{len(audit_logs) + 2000}",
        "repository_name": repo["name"],
        "decision_type": job_type,
        "input_prompt": f"Automated trigger {job_type} on branch {repo['default_branch']}",
        "ai_reasoning": reasoning,
        "proposed_diff": diff,
        "governance_passed": governance_passed,
        "governance_message": governance_message,
        "user_approved": False,
        "action_taken": "PR_OPENED" if (governance_passed and job_type in ["pr-generator", "ci-fixer"]) else ("BLOCKED" if not governance_passed else "METRICS_UPDATED"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    
    scheduler.complete_job(job_id, result, "completed" if governance_passed else "failed")
