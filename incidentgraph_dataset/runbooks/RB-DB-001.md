# Runbook RB-DB-001: DB connection pool saturation

Owner: Platform Operations
Service: settlement-worker
Trigger: DB_CONNECTION_POOL_EXHAUSTED

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Inspect active sessions and pool metrics; patch connection handling; restart worker only after approval.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-001
