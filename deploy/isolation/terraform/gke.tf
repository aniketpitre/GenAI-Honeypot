# EXAMPLE (not applied/validated here): dedicated, sandboxed node pool for the honeypot on GKE
# plus an egress firewall for its nodes. Adapt names/ranges; review before applying.
variable "project"      { type = string }
variable "region"       { type = string }
variable "cluster"      { type = string }
variable "network"      { type = string }
variable "logstash_cidr" {
  type        = string
  description = "CIDR of the Logstash/ingest endpoint the honeypot may ship logs to"
}

resource "google_container_node_pool" "honeypot" {
  project    = var.project
  location   = var.region
  cluster    = var.cluster
  name       = "honeypot"
  node_count = 1

  node_config {
    machine_type    = "e2-standard-2"
    labels          = { pool = "honeypot" }
    tags            = ["honeypot-node"]
    service_account = google_service_account.honeypot_nodes.email   # no project permissions
    oauth_scopes    = ["https://www.googleapis.com/auth/logging.write"]
    sandbox_config { sandbox_type = "gvisor" }                        # GKE Sandbox (runtime class "gvisor")
    workload_metadata_config { mode = "GKE_METADATA" }                # block node metadata credentials
    taint {
      key    = "honeypot"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }
}

resource "google_service_account" "honeypot_nodes" {
  project      = var.project
  account_id   = "honeypot-nodes"
  display_name = "Honeypot node pool (no IAM roles)"
}

# Deny all egress from honeypot nodes, then allow DNS and the log pipeline only.
resource "google_compute_firewall" "honeypot_deny_egress" {
  project            = var.project
  name               = "honeypot-deny-egress"
  network            = var.network
  direction          = "EGRESS"
  priority           = 1000
  target_tags        = ["honeypot-node"]
  destination_ranges = ["0.0.0.0/0"]
  deny { protocol = "all" }
}

resource "google_compute_firewall" "honeypot_allow_logs" {
  project            = var.project
  name               = "honeypot-allow-dns-and-logs"
  network            = var.network
  direction          = "EGRESS"
  priority           = 900
  target_tags        = ["honeypot-node"]
  destination_ranges = [var.logstash_cidr, "169.254.169.254/32"]  # metadata server is needed by GKE itself
  allow {
    protocol = "tcp"
    ports    = ["5044", "443"]
  }
  allow {
    protocol = "udp"
    ports    = ["53"]
  }
}
