---
name: Discord bot deployment readiness
description: Why this background Discord bot also exposes a minimal HTTP endpoint in production.
---

Keep a minimal HTTP endpoint returning status 200 on the Replit-assigned port when publishing this Discord bot as a VM.

**Why:** Publishing repeatedly built the image and connected to Discord successfully, but promotion still waited for an open port/readiness response and terminated the bot when none was available.

**How to apply:** Preserve the lightweight health server and its port mapping unless a future publishing target is verified to support this bot as a truly non-HTTP worker.