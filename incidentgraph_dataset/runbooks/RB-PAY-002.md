# Runbook RB-PAY-002: Gateway latency degradation

Owner: Platform Operations
Service: payment-api
Trigger: UPSTREAM_GATEWAY_TIMEOUT

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Verify gateway status; enable approved failover route; monitor retry volume.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-002
