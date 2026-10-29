# EXAMPLE (not applied/validated here): dedicated EKS managed node group for the honeypot in
# isolated subnets, with a security group that only allows the log pipeline and DNS out.
variable "cluster_name"        { type = string }
variable "honeypot_subnet_ids" { type = list(string) }
variable "vpc_id"              { type = string }
variable "node_role_arn"       { type = string }
variable "logstash_cidr"       { type = string }
variable "vpc_dns_cidr"        { type = string }  # e.g. "10.0.0.2/32" (VPC resolver)

resource "aws_security_group" "honeypot_nodes" {
  name_prefix = "honeypot-nodes-"
  vpc_id      = var.vpc_id

  # Inbound attacker traffic arrives through the Service load balancer (NodePorts).
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 5044
    to_port     = 5044
    protocol    = "tcp"
    cidr_blocks = [var.logstash_cidr]
  }
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "udp"
    cidr_blocks = [var.vpc_dns_cidr]
  }
  # Add the cluster control-plane / node-to-node rules your CNI needs; everything else is denied.
}

resource "aws_launch_template" "honeypot" {
  name_prefix            = "honeypot-"
  vpc_security_group_ids = [aws_security_group.honeypot_nodes.id]
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1          # pods cannot reach IMDS credentials
  }
}

resource "aws_eks_node_group" "honeypot" {
  cluster_name    = var.cluster_name
  node_group_name = "honeypot"
  node_role_arn   = var.node_role_arn         # least-privilege role: only what the node itself needs
  subnet_ids      = var.honeypot_subnet_ids   # private subnets with NO route to internal networks
  scaling_config {
    desired_size = 1
    min_size     = 1
    max_size     = 1
  }
  labels = { pool = "honeypot" }
  taint {
    key    = "honeypot"
    value  = "true"
    effect = "NO_SCHEDULE"
  }
  launch_template {
    id      = aws_launch_template.honeypot.id
    version = aws_launch_template.honeypot.latest_version
  }
}
