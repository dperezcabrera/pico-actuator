# Troubleshooting

## `/actuator/health` returns 404

The module was not discovered. Check:

1. `pico-actuator` is installed in the same environment as the app
   (`pip show pico-actuator`).
2. You boot with `pico_boot.init(...)`, not `pico_ioc.init(...)` — only
   pico-boot reads the `pico_boot.modules` entry point. With plain pico-ioc,
   add `pico_actuator` to `modules=` yourself.
3. Auto-discovery is not disabled (`PICO_BOOT_AUTO_PLUGINS=false` in the
   environment turns it off).

## My indicator does not show up under `components`

- The class must be decorated with `@component` **and** live in a scanned
  module (one of the `modules=` passed to `init`, or a subpackage).
- It must satisfy the protocol: a `name` attribute and a `check()` method.
  A typo like `checks()` fails silently — the class simply is not collected.

## Health returns 503 but every component says UP

`show_components: false` hides the detail while an indicator is still DOWN.
Temporarily re-enable it to see which one:

```yaml
actuator:
  show_components: true
```

## Settings from application.yaml are ignored

The YAML must be handed to the container explicitly:

```python
from pico_ioc import YamlTreeSource, configuration

config = configuration(YamlTreeSource("application.yaml"))
container = init(modules=["myapp"], config=config)
```

`init(modules=[...])` alone does not read any config file.

## An indicator reports "timed out after 5.0s"

Its `check()` exceeded `actuator.check_timeout_seconds` (default 5s). Raise
the budget for legitimately slow probes:

```yaml
actuator:
  check_timeout_seconds: 15.0
```

Or better, keep the health probe cheap and cache the expensive part (see the
[cookbook](cookbook/pattern-cached-check.md)). Note that a timed-out **sync**
check keeps running in its worker thread until it finishes on its own — the
endpoint answers, but the thread is not cancellable. Prefer async checks for
probes that can hang indefinitely.

## `/actuator/metrics` answers 501

The `metrics` extra is not installed:

```bash
pip install pico-actuator[metrics]
```
