---
name: Discord bot deployment readiness
description: Why this background Discord bot also exposes a minimal HTTP endpoint in production.
---

Keep a minimal HTTP endpoint returning status 200 on the Replit-assigned port when publishing this Discord bot as a VM. Start it before importing heavy third-party and project modules.

**Why:** Publishing repeatedly built the image and connected to Discord successfully, but promotion still waited for an open port/readiness response. Starting the endpoint after application imports also produced a roughly 24-second burst of connection-refused and status-500 health checks.

**How to apply:** Preserve the lightweight health server, early startup order, and port mapping unless a future publishing target is verified to support this bot as a truly non-HTTP worker.