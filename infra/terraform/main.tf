provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "autopilot" {
  metadata {
    name = "repo-autopilot"
  }
}

# Add other core infrastructure elements as needed (EKS clusters, RDS instances, etc.)
