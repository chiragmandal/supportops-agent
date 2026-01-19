# Troubleshooting (Fintech SaaS)

## Common issues
- Transactions stuck in "pending": may take up to 30 minutes due to provider processing.
- Webhooks failing: verify endpoint URL, secrets, and check retry logs in Developer Settings.
- API errors: ask for request_id, timestamp, and endpoint.

## Performance
- Dashboard latency: check status page for incidents and ask for region.

## Data export
- CSV exports over 50k rows are processed asynchronously; user receives an email when ready.
