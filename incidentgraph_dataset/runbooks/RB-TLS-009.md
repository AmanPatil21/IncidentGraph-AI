# Runbook RB-TLS-009: Expired TLS certificate

Owner: Platform Operations
Service: webhook-dispatcher
Trigger: TLS_CERT_EXPIRED

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Rotate certificate; validate trust chain; replay queued deliveries with approval.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-009
