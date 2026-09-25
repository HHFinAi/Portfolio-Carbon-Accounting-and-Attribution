# Holdings, denominators and scope

## Decision context
What emissions are financed by the scoped holdings, how complete is the data, and why did the measured inventory change?

## Assignment
Reconcile accounting perimeter, position IDs and issuer IDs. Aggregate positions in one issuer before attribution; reconcile joint equity/debt holdings. Inputs must use a common currency and scale. Exclude unsupported instruments explicitly, with the excluded portfolio value reported, not hidden.

## Required output sections
- `position_reconciliation`: substantive analysis linked to claim IDs.
- `entity_mapping`: substantive analysis linked to claim IDs.
- `asset_class_boundary`: substantive analysis linked to claim IDs.
- `currency_and_period`: substantive analysis linked to claim IDs.

## Evidence and methodology
Use PCAF-2025 with edition, applicability, date and limitations. Source references are in `references/standards.json` from the repository root.

## Return contract
Return the structured artifact in `schemas/artifact.schema.json`; copy run_id, input_digest, stage_id and revision from the current packet. Never recycle IDs from a demo. Source uncertainty is not resolved by lowering confidence alone: preserve a gap or issue.

## Domain boundary
Executable accounting is limited to long-only listed-company equity and corporate-debt EVIC inputs, not all PCAF asset classes. No short-netting, derivatives, sovereign GDP denominator, nature credits, or avoided-emissions offsets. Methodology changes and scope restatements require manual reconciliation.
