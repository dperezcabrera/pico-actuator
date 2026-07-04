# Cookbook: Securing Actuator Endpoints

Goal: keep `/actuator/*` reachable for orchestrators and operators but not for
the public internet. Health payloads leak topology (component names, error
messages, versions) — treat them as internal.

## Option 1: Do not expose them (preferred)

If the app sits behind an ingress/reverse proxy, block the prefix at the edge
and let probes reach the pod directly (kubelet probes bypass the ingress):

```nginx
# nginx
location /actuator/ { deny all; return 404; }
```

```yaml
# traefik: route only /api to the public entrypoint; actuator stays cluster-internal
```

Nothing to code — the endpoints stay fully open inside the cluster, which is
what kubelet needs.

## Option 2: Guard them in-app

When there is no trusted edge, add a `FastApiConfigurer` (a pico-fastapi
protocol, collected automatically like indicators) that installs a small
middleware:

```python
import secrets

from pico_ioc import component
from starlette.responses import JSONResponse


@component
class ActuatorGuard:  # satisfies FastApiConfigurer
    def __init__(self, settings: SecuritySettings):
        self.token = settings.actuator_token

    def configure(self, app):
        @app.middleware("http")
        async def guard(request, call_next):
            if request.url.path.startswith("/actuator") and request.url.path != "/actuator/health/live":
                supplied = request.headers.get("x-actuator-token", "")
                if not secrets.compare_digest(supplied, self.token):
                    return JSONResponse({"detail": "forbidden"}, status_code=403)
            return await call_next(request)
```

Probes then send the header:

```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/ready
    port: 8000
    httpHeaders:
      - name: x-actuator-token
        value: "<from a Secret>"
```

## Notes

- **Leave `/health/live` open.** It reveals nothing (`{"status":"UP"}`) and
  keeping it token-free means a rotated secret can never cause a restart storm.
- **`secrets.compare_digest`**, not `==` — constant-time comparison.
- **Least detail off-cluster:** if the payload must cross a boundary, set
  `actuator.show_components: false` and keep the detail for internal calls.
