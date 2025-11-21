---
noteId: "12952cc0c5a411f0ac47819087bbe0ed"
tags: []

---

> [!IMPORTANT]
> **Reference Only**: This runbook describes the operational procedures for a full **Production GCP Deployment**. The current repository is a **Local-First Demo** using DuckDB. This document serves as a reference for how the system would be operated if deployed to GCP.

# Retail Copilot Runbook
# Operational procedures for incident response, monitoring, and maintenance

## Version
- **Version**: 1.0
- **Last Updated**: 2025-01-01
- **Owner**: MLE / Data Engineer

## Quick Reference

### On-Call Contacts
- **Primary**: MLE Team Lead
- **Secondary**: Data Engineer
- **Escalation**: Solutions Architect

### Service URLs
- **API Gateway**: `https://api.retail-copilot.example.com`
- **Monitoring Dashboard**: `https://monitoring.example.com/copilot`
- **Logs**: Cloud Logging → `retail-copilot-*`

## Incident Response

### Severity Levels
- **P0 (Critical)**: Service down, data breach, all tenants affected
- **P1 (High)**: Partial outage, high error rate (>5%), single tenant affected
- **P2 (Medium)**: Degraded performance, elevated latency (>p95)
- **P3 (Low)**: Minor issues, non-blocking

### P0: Service Down
**Symptoms**: All API requests returning 5xx errors

**Actions**:
1. Check Cloud Run service status: `gcloud run services describe copilot-api`
2. Check Vertex AI endpoint status: `gcloud ai endpoints list`
3. Check BigQuery quota/exceeded: `gcloud logging read "resource.type=bigquery_project"`
4. **Rollback**: If recent deployment, rollback to previous revision
   ```bash
   gcloud run services update-traffic copilot-api --to-revisions=revision-001=100
   ```
5. **Escalate**: If rollback doesn't resolve, escalate to Solutions Architect

### P1: High Error Rate
**Symptoms**: Error rate > 5%, latency > p95 threshold

**Actions**:
1. Check error logs: `gcloud logging read "severity>=ERROR" --limit=50`
2. Identify error pattern:
   - SQL validation failures → Check `sql/` policies
   - LLM timeout → Check Vertex endpoint latency
   - BigQuery quota → Check slot usage
3. Check recent changes: `git log --since="24 hours ago" -- prompts/ sql/`
4. **Mitigation**: 
   - If prompt/template issue: Rollback prompt version
   - If BigQuery issue: Increase slot reservation
   - If LLM issue: Switch to fallback model or reduce temperature
5. **Auto-revert**: If canary deployment active, auto-revert on SLO breach

### P2: Degraded Performance
**Symptoms**: Latency p95 > 2.0s but < 3.0s, error rate < 5%

**Actions**:
1. Check monitoring dashboard for trends
2. Review recent query patterns: `SELECT * FROM copilot_usage.queries WHERE created_at > NOW() - INTERVAL 1 HOUR`
3. Check cost per query: Alert if > $0.01
4. **Mitigation**: 
   - Optimize slow queries (add indexes, reduce scan size)
   - Scale Cloud Run instances if cold starts
   - Check BigQuery slot usage

### P3: Minor Issues
**Symptoms**: Non-blocking, user-reported issues

**Actions**:
1. Log issue in ticketing system
2. Review golden set for regression
3. Check user feedback: `SELECT * FROM copilot_feedback.events WHERE issue_type IS NOT NULL`

## Monitoring & Alerts

### Key Metrics Dashboard
- **Latency**: p50, p95, p99 (target: p95 < 2.0s)
- **Error Rate**: Target < 1%
- **Cost per Answer**: Target p95 < $0.01
- **Golden Set Pass Rate**: Target > 80%
- **Faithfulness Score**: Target > 0.75

### Alert Thresholds
- **Latency p95 > 3.0s**: Page on-call
- **Error Rate > 5%**: Page on-call
- **Cost per Answer > $0.02**: Alert (non-page)
- **Golden Set Pass Rate < 70%**: Alert (non-page)
- **Budget Daily > 80%**: Alert (non-page)

### Log Queries

#### Find high-latency queries
```sql
SELECT 
  request_id,
  intent_id,
  latency_ms,
  bytes_processed
FROM copilot_usage.queries
WHERE created_at > NOW() - INTERVAL 1 HOUR
  AND latency_ms > 2000
ORDER BY latency_ms DESC
LIMIT 10;
```

#### Find SQL validation failures
```sql
SELECT 
  request_id,
  user_query,
  error_message,
  sql_candidate
FROM copilot_audit.logs
WHERE severity = "ERROR"
  AND error_message LIKE "%validation%"
  AND created_at > NOW() - INTERVAL 1 HOUR;
```

#### Find high-cost queries
```sql
SELECT 
  request_id,
  tenant_id,
  intent_id,
  bytes_processed,
  cost_usd
FROM copilot_cost.usage
WHERE created_at > NOW() - INTERVAL 1 HOUR
  AND cost_usd > 0.01
ORDER BY cost_usd DESC;
```

## Deployment Procedures

### Pre-Deployment Checklist
- [ ] All unit tests pass: `pytest tests/`
- [ ] Golden set pass rate > 80%: `python scripts/aggregate_eval.py`
- [ ] SQL lints pass: `python scripts/check_sql_lints.py`
- [ ] Promotion gates pass: `python scripts/check_gates.py --metrics metrics.json`
- [ ] Rollback plan documented

### Canary Deployment
1. Deploy to 5% traffic
2. Monitor for 2 hours:
   - Error rate
   - Latency p95
   - Cost per answer
   - Golden set regression
3. If stable, increase to 25% → 50% → 100% over 24 hours
4. **Auto-revert** if:
   - Error rate > baseline + 5%
   - Latency p95 > baseline + 20%
   - Cost per answer > baseline + 20%

### Rollback Procedure
```bash
# Rollback Cloud Run revision
gcloud run services update-traffic copilot-api \
  --to-revisions=previous-revision=100

# Rollback Vertex AI endpoint (if model changed)
gcloud ai endpoints update ENDPOINT_ID \
  --traffic-split=model-v1=100,model-v2=0

# Rollback prompt version (config flag)
# Update config map to previous prompt hash
kubectl set env deployment/copilot-api PROMPT_VERSION=v1
```

## Maintenance Tasks

### Weekly
- Review golden set pass rate
- Review user feedback
- Check cost trends
- Review error logs for patterns

### Monthly
- Update golden set (add new intents/paraphrases)
- Review and update glossary
- Review SQL templates for optimization
- Review promotion gates thresholds

### Quarterly
- Review architecture and SLOs
- Update runbook based on incidents
- Review tenancy model and RLS policies
- Review cost budgets and alert thresholds

## Troubleshooting

### SQL Generation Failures
**Symptoms**: "No valid SQL generated" errors

**Debug**:
1. Check planner output: `SELECT plan_json FROM copilot_audit.logs WHERE request_id = '...'`
2. Check template availability: `ls sql/templates/`
3. Check glossary hits: Verify terms are in `catalog/glossary.md`

**Fix**:
- Update glossary if term missing
- Add new template if intent not covered
- Check planner prompt version

### High Latency
**Symptoms**: p95 > 2.0s

**Debug**:
1. Check BigQuery query time: `SELECT query_time_ms FROM copilot_usage.queries`
2. Check LLM latency: `SELECT llm_latency_ms FROM copilot_usage.queries`
3. Check Cloud Run cold starts

**Fix**:
- Optimize SQL (add partitions, reduce scan size)
- Use faster LLM model (Gemini Flash vs Pro)
- Increase Cloud Run min instances
- Cache frequent queries

### Cost Overruns
**Symptoms**: Daily cost > budget

**Debug**:
1. Identify high-cost queries: See log queries above
2. Check for runaway scans: `SELECT bytes_processed FROM copilot_cost.usage WHERE bytes_processed > 10GB`
3. Check LLM token usage: `SELECT tokens_in, tokens_out FROM copilot_cost.usage`

**Fix**:
- Enforce stricter LIMIT clauses
- Reduce max_bytes_billed per query
- Optimize prompts to reduce token usage
- Add cost alerts at 50%, 80% of budget

## Emergency Contacts
- **GCP Support**: [Support Portal]
- **Vertex AI Team**: [Internal Slack]
- **BigQuery Team**: [Internal Slack]

