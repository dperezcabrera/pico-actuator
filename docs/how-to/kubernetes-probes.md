# Kubernetes Probes

The three health endpoints map directly onto Kubernetes probes:

| Endpoint | Probe | Semantics |
|---|---|---|
| `/actuator/health/live` | `livenessProbe` | Process is responding. Never checks dependencies — a dead database must not get your pod restarted. |
| `/actuator/health/ready` | `readinessProbe` | Dependencies are healthy; `503` takes the pod out of the Service until they recover. |
| `/actuator/health` | dashboards / humans | Full per-component detail. |

```yaml
# deployment.yaml (container spec)
livenessProbe:
  httpGet:
    path: /actuator/health/live
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /actuator/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Rules of thumb

- Put **only dependencies you can recover from** behind readiness (database,
  message broker). A pod that is `NotReady` stops receiving traffic but keeps
  running — that is what you want during a database hiccup.
- Never point the liveness probe at `/health` or `/health/ready`: a slow
  dependency would restart perfectly healthy pods in a loop.
