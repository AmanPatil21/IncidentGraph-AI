# Runbook RB-RATE-007: Partner API rate limiting

Owner: Platform Operations
Service: payout-service
Trigger: RATE_LIMIT_429

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Throttle polling; implement exponential backoff; coordinate with partner.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-007
