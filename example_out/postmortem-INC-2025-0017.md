
# Postmortem: Checkout API elevated 5xx errors
- **Incident ID:** INC-2025-0017
- **Status:** RESOLVED
- **Severity:** SEV-2
- **Service:** checkout-api (production)
- **Owner Team:** Payments Platform
- **Start:** 2025-12-18 13:07:00+00:00 (UTC)
- **End:** 2025-12-18 14:02:00+00:00 (UTC)
- **Detected:** 2025-12-18 13:10:00+00:00 (UTC)
- **Mitigated:** 2025-12-18 13:28:00+00:00 (UTC)

---

## Summary

### What happened
Beginning at 13:07 UTC, the checkout-api began returning elevated 5xx errors. The issue was triggered by a misconfigured database connection pool limit introduced in a configuration rollout. Error rates peaked at ~18% before mitigation.


### User impact
A subset of users were unable to complete checkout. Some requests succeeded after retries, but many experienced failures on initial attempt.


### Duration
- **Duration (minutes):** 55

---

## Impact

- **Customers affected (estimate):** 8200
- **Regions affected:** us-east-1
- **Peak error rate:** 18.2%
- **Peak p95 latency:** 2400 ms
- **Business impact:** Increased checkout failures reduced conversion rate during the incident window.


### SLA/SLO
- **SLO breached:** Yes
- **SLO name:** Checkout Success Rate (30d rolling)
- **Breach window:** 2025-12-18T13:12:00Z to 2025-12-18T13:31:00Z

---

## Detection

- **Detected by:** monitoring_alert

### Signals
- **Prometheus — checkout_api_5xx_rate:** Alert fired when 5xx rate exceeded 5% for 5 minutes.
- **Datadog — p95_latency:** Latency SLO burn rate increased sharply.

### Customer reports
- **Count:** 34
- **Channels:** support_chat, email

### Gaps
- Alert thresholds did not capture gradual error-rate increases early enough.

---

## Timeline (UTC)

- **2025-12-18 13:07:00+00:00** — *trigger* — **deploy-bot**: Config rollout started for checkout-api (db pool changes).
  - Deployment: https://example.com/deploy/12345
- **2025-12-18 13:10:00+00:00** — *detection* — **oncall**: 5xx alert fired; on-call acknowledged.
- **2025-12-18 13:14:00+00:00** — *investigation* — **oncall**: Initial triage: DB connection saturation observed; error spikes correlate with rollout.
- **2025-12-18 13:18:00+00:00** — *investigation* — **payments-team**: Confirmed db pool limit reduced from 80 → 20 in config; connections queueing.
- **2025-12-18 13:22:00+00:00** — *mitigation* — **oncall**: Paused rollout and began config rollback.
- **2025-12-18 13:28:00+00:00** — *mitigation* — **deploy-bot**: Rollback completed; error rate trending down.
- **2025-12-18 13:35:00+00:00** — *comms* — **incident-commander**: Status page updated: investigating elevated errors in checkout.
  - Status Page: https://status.example.com/incidents/abcd
- **2025-12-18 14:02:00+00:00** — *recovery* — **oncall**: Service stable; error rate back to baseline; incident resolved.

---

## Root Cause

### Direct cause
A configuration change reduced the database connection pool limit, causing connection starvation and increased 5xx errors under normal load.


### Contributing factors
- Config rollout did not include a guardrail check for pool-size reduction.
- No canary analysis on connection saturation metrics before full rollout.

### Why it was not prevented
The configuration pipeline lacked policy checks for risky parameter changes, and runbooks did not include a pre-rollout review step for connection pool settings.


---

## Response

### What worked well
- Monitoring detected the issue within minutes.
- Rollback procedure was executed quickly and safely.
- On-call escalation to service owners was fast.

### What did not work well
- Initial alerting did not capture early gradual increases.
- No automated rollback on SLO burn rate.

### Where we got lucky
- Rollback fully restored service without requiring a DB restart.

---

## Communication

### Internal
- **Channel:** #incidents
- **Started at:** 2025-12-18 13:12:00+00:00

### External
- **Status page used:** Yes
- **First update at:** 2025-12-18 13:35:00+00:00
- **Updates count:** 2

**Customer message:**
We investigated elevated error rates affecting checkout and rolled back a configuration change. Service has returned to normal operation.


---

## Action Items

| ID | Title | Owner | Priority | Due | Type | Status |
|---|---|---|---|---|---|---|
| AI-001 | Add policy checks for risky DB pool configuration changes | payments-platform | P0 | 2026-01-05 | prevention | open |
| AI-002 | Add canary analysis for DB saturation metrics during rollout | sre | P1 | 2026-01-12 | detection | open |
| AI-003 | Update runbook: pre-rollout review checklist for connection pool settings | payments-team | P2 | 2026-01-20 | documentation | open |

**AI-001 Success Criteria:** Config pipeline blocks pool-size reductions >25% without approval.
- AI-001 — Tracking Ticket: https://example.com/jira/AI-001
**AI-002 Success Criteria:** Rollouts auto-halt on sustained connection saturation for 3 minutes.
**AI-003 Success Criteria:** Runbook includes checklist and rollback steps with owners.

---

## References

### Dashboards
- Checkout API Overview: https://example.com/dashboards/checkout

### Logs
- checkout-api logs: https://example.com/logs/checkout

### Runbooks
- Checkout On-Call Runbook: https://example.com/runbooks/checkout

---

## Tags
config, database, rollout, slo
