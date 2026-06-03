# Security Detection

Documents the security monitoring controls in this project — what threat each signal maps to, how to tune it, and what the false-positive risks are.

---

## Monitoring vs detection

Monitoring answers: *is the system up?*
Detection answers: *is the system under attack?*

The same Prometheus stack handles both — the difference is the intent behind the alert rules. A `ContainerRestartAnomaly` alert is not an SRE availability alert; it is a detection signal for crash-loops caused by exploit payloads or adversarial container cycling.

---

## Signals

### 1. Auth failure spike (401/403)

| | |
|---|---|
| **Threat** | Brute-force, credential stuffing, account enumeration |
| **Metric** | `http_requests_total{status=~"401\|403"}` (app-level exporter) |
| **Rule** | Rate > 10/s sustained for 2 min |
| **False-positive risk** | A misconfigured client, a broken CI integration, or a token rotation can produce a burst of 401s. Tune the threshold to your observed baseline before enabling in production. |
| **What to do when it fires** | Check source IPs in access logs; correlate with Gitleaks to rule out a leaked credential; rotate credentials if a real account is being targeted. |
| **Limitation** | Requires the app to export Prometheus metrics (`prometheus_flask_exporter` or equivalent). Not available by default. |

---

### 2. Container restart anomaly

| | |
|---|---|
| **Threat** | Crash-loop from exploit payload, OOM from DoS, adversarial container cycling |
| **Metric** | `container_start_time_seconds` (cAdvisor) |
| **Rule** | `changes()` > 2 in 10 min |
| **False-positive risk** | OOM kills from legitimate workloads, bad config during a deploy, or a flapping healthcheck will trigger this. Correlate with memory metrics and deployment events before treating as hostile. |
| **What to do when it fires** | `docker logs <container>` for the exit reason; check if an OOM kill happened; if restarts are paired with unusual outbound traffic (signal 3), treat as hostile. |
| **Limitation** | `changes()` resets after the 10-min window — a slow restart pattern spread over 20 min may not fire. |

---

### 3. High outbound network traffic

| | |
|---|---|
| **Threat** | Data exfiltration, C2 beacon, cryptominer outbound connections |
| **Metric** | `container_network_transmit_bytes_total` (cAdvisor) |
| **Rule** | Rate > 10 MB/s sustained for 5 min |
| **False-positive risk** | A legitimate backup job, large file upload, or bulk API call will look identical. The threshold of 10 MB/s is conservative for a dev-sized app — tune down to your normal peak. |
| **What to do when it fires** | `netstat -tnp` inside the container; check destination IPs against threat intel; if unknown external IPs, isolate the container immediately. |
| **Limitation** | Measures bytes transmitted, not connection count or destination. A low-bandwidth C2 beacon (common in real APTs) will not fire this alert. Network-level detection (firewall logs, DNS monitoring) is required to catch that pattern. |

---

## How to run locally

```bash
cd monitoring
docker compose up -d

# Prometheus:   http://localhost:9090
# Alertmanager: http://localhost:9093
# Grafana:      http://localhost:3000  (admin / changeme)
```

Import `dashboards/security.json` via Grafana → Dashboards → Import.

Add a Prometheus data source pointing at `http://prometheus:9090`.

---

## Simulating an alert (container restart)

```bash
# Run a container that exits immediately — triggers ContainerRestartAnomaly
docker run --restart=always --name crasher alpine sh -c "exit 1"

# Watch in Prometheus:
# changes(container_start_time_seconds{name="crasher"}[10m])

# Clean up:
docker stop crasher && docker rm crasher
```

---

## Interview answer

> *"I extended an existing Prometheus/Grafana stack to emit security signals rather than just availability signals. The same cAdvisor metrics that tell you a container is consuming CPU tell you it is restarting suspiciously. The difference is in the alert rule and the annotation — I label each rule with the threat it maps to and what to do when it fires. The hardest part is threshold tuning: an alert that fires on every deploy teaches teams to ignore it, which is worse than no alert at all."*
