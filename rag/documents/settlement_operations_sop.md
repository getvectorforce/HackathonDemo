# SOP: Settlement, Ledger Operations & Restitution

## Section 1: Core Ledger Reversals
- **Immediate Reversal Posting**: Upon sign-off from Fraud Containment and Underwriting, settlement operations posts a temporary offsetting credit to general ledger account `GL-7102 (Disputed Clearing)` and deposits provisional credit into customer account `DDA`.
- **Card Network Chargeback**: Initiate Visa/Mastercard dispute reason code `10.4 (Other Fraud: Card-Absent Environment)` or `4837 (No Cardholder Authorization)`.
- **ACH Return Codes**:
  - `R10`: Customer Advises Unauthorized, Improper, Ineligible, or Notice Not Provided. Return time window: 60 calendar days from settlement.
  - `R07`: Authorization Revoked by Customer.

## Section 2: Account Restitution and Credentials Replacement
- Issue new Virtual Debit Card (VDC) immediately in the mobile app container.
- Update digital wallet tokenization (Apple Pay / Google Wallet) with modern token lifecycle management.
- Generate incident resolution ticket `RESTITUTION-COMPLETE` and notify customer triage agent.

