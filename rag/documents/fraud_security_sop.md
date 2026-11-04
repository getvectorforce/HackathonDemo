# SOP: Fraud Detection, Risk Scoring & Incident Escalation

## Section 1: Geo-Velocity and Anomaly Detection Rules
- **Impossible Travel / Geo-Velocity**: An alert triggers when transactions occur in distinct geographical regions without sufficient physical travel time between timestamps (e.g., login in New York at 10:00 AM, card transaction in Bucharest at 10:45 AM).
- **High-Risk Merchant Categories**: Foreign luxury retail, cryptocurrency exchanges, wire service bureaus, and automated gift card kiosks trigger an elevated risk score (+35 points).
- **Composite Risk Score (CRS)**:
  - 0-29: Low Risk (Standard monitoring)
  - 30-69: Medium Risk (Step-up authentication required)
  - 70-100: High Risk (Immediate containment required: freeze card, invalidate session tokens, lock outbound transfers)

## Section 2: Containment Protocol
1. **Immediate Card Isolation**: Place a `HARD_FREEZE` on the affected debit/credit PAN.
2. **Session Invalidation**: Revoke all active OAuth refresh tokens and terminate mobile/web banking sessions.
3. **MFA Reset & Verification**: Flag customer profile for mandatory out-of-band biometric or phone verification prior to unlocking online access.
4. **Handoff Requirement**: Once containment is placed, notify the Credit Underwriting and Settlement operations teams to handle dispute credits and pending auto-debits.

