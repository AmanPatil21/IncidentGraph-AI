# Runbook RB-ML-006: Missing model artifact

Owner: Platform Operations
Service: fraud-scoring
Trigger: MODEL_ARTIFACT_NOT_FOUND

## Diagnostic checklist
1. Confirm incident time window, affected service and error code.
2. Inspect service logs and compare the last known healthy deployment.
3. Check upstream/downstream job dependencies.
4. Correlate metrics with configuration and deployment history.

## Recommended response
Validate artifact registry path; roll back model pointer after approval.

## Safety and escalation
Never perform production rollback, financial replay, credential changes, or external side effects without an authorized operator's approval. Escalate unresolved incidents to the service owner.

## Related incident
INC-006
