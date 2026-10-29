"""Downloadable lure files whose use calls the canary: a fake AWS credentials
file (endpoint_url redirects every SDK/CLI call to the listener) and a fake
kubeconfig (kubectl's `server` points at the listener). The keys/tokens are
random and inert."""
import secrets
import string

_UP = string.ascii_uppercase + string.digits
_B64 = string.ascii_letters + string.digits + "+/"


def aws_credentials(trap_url: str, profile: str = "prod-admin") -> str:
    key_id = "AKIA" + "".join(secrets.choice(_UP) for _ in range(16))
    secret = "".join(secrets.choice(_B64) for _ in range(40))
    return (
        f"[{profile}]\n"
        f"aws_access_key_id = {key_id}\n"
        f"aws_secret_access_key = {secret}\n"
        f"region = us-east-1\n"
        f"endpoint_url = {trap_url}\n"
    )


def kubeconfig(trap_url: str, cluster: str = "prod-eu1") -> str:
    token = "eyJhbGciOiJSUzI1NiIs" + secrets.token_urlsafe(48)
    return (
        "apiVersion: v1\n"
        "kind: Config\n"
        f"current-context: {cluster}-admin\n"
        "clusters:\n"
        f"- name: {cluster}\n"
        f"  cluster:\n    server: {trap_url}\n"
        "users:\n"
        f"- name: {cluster}-admin\n"
        f"  user:\n    token: {token}\n"
        "contexts:\n"
        f"- name: {cluster}-admin\n"
        f"  context: {{cluster: {cluster}, user: {cluster}-admin}}\n"
    )
