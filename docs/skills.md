# AI Coding Skills

[Claude Code](https://code.claude.com) and [OpenAI Codex](https://openai.com/index/introducing-codex/) skills for AI-assisted development with pico-actuator.

## Installation

```bash
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash -s -- actuator
```

Or install all pico skills:

```bash
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash
```

### Platform-specific

```bash
# Claude Code only
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash -s -- --claude actuator

# OpenAI Codex only
curl -sL https://raw.githubusercontent.com/dperezcabrera/pico-skills/main/install.sh | bash -s -- --codex actuator
```

## What the skill covers

- Adding a `HealthIndicator` / `InfoContributor` to an existing app
- The failure-isolation and status-code contract of the endpoints
- Wiring `/health/live` and `/health/ready` into Kubernetes probes
- Testing indicators and endpoints (see [Testing](how-to/testing.md))
