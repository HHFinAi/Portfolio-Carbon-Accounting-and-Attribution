# Investment-decision handoff

## Decision context
What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change?

## Assignment
Connect the analytical findings to an identified instrument or portfolio decision. Separate attractive economics from mandate permission. Document price, valuation, entry conditions, downside, catalysts, liquidity, hedging and thesis breakers. PUBLIC/PRIVATE_MARKET_CANDIDATE requires every declared check to pass and reviewed quote/contract evidence; otherwise RESEARCH_ONLY or NO_INVESTMENT_ROUTE. No execution authority.

## Required output sections
- `valuation_and_entry`: substantive analysis linked to claim IDs.
- `risk_catalysts_and_thesis_breakers`: substantive analysis linked to claim IDs.
- `eligibility_review`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use the mandate and registered primary evidence with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
