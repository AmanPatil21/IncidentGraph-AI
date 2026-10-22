# Runbook RB-QUEUE-005: Insufficient queue consumers

Owner: Platform Operations
Service: notification-worker
Trigger: QUEUE_CONSUMER_LAG

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Inspect HPA settings; restore approved replica minimum; verify queue drains.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-005
