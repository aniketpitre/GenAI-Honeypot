# Honeypot isolation

The chart gives the honeypot pod: no service-account token, dropped capabilities, `runtimeClassName`,
node selector/tolerations, and a NetworkPolicy that allows only DNS, the API and Logstash. This
folder adds the pieces that live outside the chart. Treat the honeypot as **already compromised**.

| File | What it does | Verified here |
|---|---|---|
| `kubernetes.yaml` | gVisor `RuntimeClass`, `deception` namespace with Pod Security labels (baseline enforced), namespace default-deny | schema-validated |
| `cilium-honeypot-egress.yaml` | optional explicit egress allow-list for Cilium (drops show in Hubble) | schema-validated |
| `terraform/gke.tf` | sandboxed (gVisor) dedicated node pool, no-IAM node service account, egress-deny firewall + log allow | **example, not applied** |
| `terraform/aws.tf` | dedicated EKS node group in isolated subnets, restrictive SG, IMDSv2 hop-limit 1 | **example, not applied** |

Checklist before exposing the honeypot:
1. Dedicated node pool/VPC subnets with **no route** to production networks or private endpoints.
2. gVisor/Kata runtime on that pool (`honeypot.runtimeClassName=gvisor`).
3. Cloud egress firewall as the second layer (Terraform examples) — NetworkPolicy alone is not enough if the CNI is bypassed.
4. Block the instance metadata service (IMDSv2 hop-limit 1 / GKE metadata concealment).
5. Alert on any *dropped egress* from the honeypot pod (Hubble/VPC flow logs): it is a strong signal of a post-exploitation attempt.
6. Rebuild nodes on a schedule; never reuse the honeypot's credentials or data anywhere else.
