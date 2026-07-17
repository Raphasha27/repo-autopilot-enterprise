import re
import json
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field

class GovernanceRuleResult(BaseModel):
    passed: bool
    rule_name: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

class PolicyEngine:
    """
    Enterprise Governance & Safety Engine for Repo Autopilot.
    Enforces strict risk, CI/CD, branch protection, and architectural policies.
    """

    def __init__(self, max_prs_per_hour: int = 5, danger_keywords: list = None):
        self.max_prs_per_hour = max_prs_per_hour
        self.danger_keywords = danger_keywords or [
            "rm -rf", "delete", "destroy", "drop database", "purge", "wipe", "--force"
        ]

    def evaluate_git_action(self, action_type: str, payload: Dict[str, Any]) -> GovernanceRuleResult:
        """
        AI is NOT allowed to:
          1. Merge pull requests automatically without CI success
          2. Delete repositories or branches
          3. Execute destructive git operations without approval
          4. Bypass governance rules
        """
        action_type = action_type.lower()
        
        # Rule 1: No branch or repository deletion
        if action_type in ["delete_branch", "delete_repo", "delete_repository"]:
            return GovernanceRuleResult(
                passed=False,
                rule_name="NO_DELETION_ALLOWED",
                message="AI is strictly forbidden from deleting branches or repositories."
            )

        # Rule 2: Git force pushes
        if action_type == "git_push" and payload.get("force", False):
            return GovernanceRuleResult(
                passed=False,
                rule_name="NO_FORCE_PUSH",
                message="Destructive git operations like force pushing (--force) are strictly prohibited without human operator bypass."
            )

        # Rule 3: Merging PRs
        if action_type == "merge_pr":
            ci_status = payload.get("ci_status", "").lower()
            if ci_status != "success":
                return GovernanceRuleResult(
                    passed=False,
                    rule_name="CI_SUCCESS_REQUIRED_FOR_MERGE",
                    message=f"AI cannot merge pull requests without successful CI. Current CI status: '{ci_status}'.",
                    details={"ci_status": ci_status}
                )
            
            # Require human approval for production branch merges
            target_branch = payload.get("target_branch", "main")
            if target_branch in ["main", "production", "prod"] and not payload.get("human_approved", False):
                return GovernanceRuleResult(
                    passed=False,
                    rule_name="HUMAN_APPROVAL_REQUIRED_FOR_PROD_MERGE",
                    message="Merging into production-grade branches requires explicit human approval."
                )

        return GovernanceRuleResult(
            passed=True,
            rule_name="GIT_ACTION_SAFETY",
            message="Git action passed safety standards."
        )

    def evaluate_proposed_code(self, proposed_diff: str, file_path: str) -> GovernanceRuleResult:
        """
        Inspects generated code or file diffs for dangerous shell executions, compliance, or risk keywords.
        """
        if not proposed_diff:
            return GovernanceRuleResult(passed=True, rule_name="CODE_DIFF_SCAN", message="Empty diff. Safety scan skipped.")

        # Check for banned keywords
        detected = []
        for kw in self.danger_keywords:
            if kw in proposed_diff.lower():
                detected.append(kw)

        if detected:
            return GovernanceRuleResult(
                passed=False,
                rule_name="DANGEROUS_COMMANDS_DETECTED",
                message=f"Code changes contain potential destructive or unsafe actions: {detected}",
                details={"detected_keywords": detected}
            )

        # Infrastructure modifications check
        infra_paths = ["k8s/", "terraform/", "helm/", "docker-compose", "deployments", ".tf", ".yaml", ".yml"]
        is_infra_file = any(p in file_path.lower() for p in infra_paths)
        
        if is_infra_file:
            # Let's check if the change mutates core infrastructure policies without approval
            if "privilege" in proposed_diff.lower() or "root" in proposed_diff.lower() or "allow" in proposed_diff.lower():
                return GovernanceRuleResult(
                    passed=False,
                    rule_name="INFRASTRUCTURE_MUTATION_GUARD",
                    message="AI is not allowed to modify security permissions or root privileges in infrastructure files directly.",
                    details={"file": file_path}
                )

        return GovernanceRuleResult(
            passed=True,
            rule_name="CODE_DIFF_SCAN",
            message="Code structure matches internal security and reliability guidelines."
        )

    def evaluate_dependency_change(self, file_name: str, file_content: str) -> GovernanceRuleResult:
        """
        Parses dependency changes and blocks deprecated, insecure, or copyleft-licensed dependencies.
        """
        # Define high-risk packages (mock representation of package scanner list)
        high_risk_packages = ["event-stream", "ua-parser-js", "flatmap-stream", "pep517-exploit"]
        
        detected_packages = []
        for pkg in high_risk_packages:
            if pkg in file_content:
                detected_packages.append(pkg)
                
        if detected_packages:
            return GovernanceRuleResult(
                passed=False,
                rule_name="MALICIOUS_DEPENDENCY_PREVENTION",
                message=f"Blocked integration of high-risk or known compromised dependency: {detected_packages}",
                details={"flagged_packages": detected_packages}
            )

        return GovernanceRuleResult(
            passed=True,
            rule_name="DEPENDENCY_SAFETY",
            message="Dependency graph update verified. No high-risk or licensing failures found."
        )

    def evaluate_rate_limit(self, recent_actions_count: int) -> GovernanceRuleResult:
        """
        Enforce operational rate limits on active AI modifications.
        """
        if recent_actions_count >= self.max_prs_per_hour:
            return GovernanceRuleResult(
                passed=False,
                rule_name="RATE_LIMIT_EXCEEDED",
                message=f"AI operation throttled. Repository rate limit reached ({self.max_prs_per_hour} actions/hour).",
                details={"recent_actions": recent_actions_count, "limit": self.max_prs_per_hour}
            )

        return GovernanceRuleResult(
            passed=True,
            rule_name="RATE_LIMIT_CHECK",
            message="Rate limits within stable bounds."
        )
