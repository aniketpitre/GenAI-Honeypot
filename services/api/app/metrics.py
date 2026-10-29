from prometheus_client import Counter

HITS = Counter("deception_hits_total", "Canary hits received from the listener", ["result"])
EVENT_PUBLISH_FAILURES = Counter(
    "deception_event_publish_failures_total", "Failed event deliveries", ["target"]
)
