---
name: Discord bot deployment readiness
description: Why this background Discord bot also exposes a minimal HTTP endpoint in production.
---

Keep a minimal HTTP endpoint returning status 200 on the configured local port 8080 when publishing this Discord bot as a VM. Start it before importing heavy third-party and project modules.

**Why:** Publishing repeatedly built the image and connected to Discord successfully, but promotion still waited for an open port/readiness response. Starting late caused readiness failures, and binding to the production `PORT` environment value did not match the explicit `.replit` local-port mapping.

**How to apply:** Preserve the lightweight health server, early startup order, and explicit 8080 port mapping unless a future publishing target is verified to support this bot as a truly non-HTTP worker.