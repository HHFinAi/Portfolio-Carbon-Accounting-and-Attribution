# Worked example — Portfolio Carbon Accounting and Attribution Agent

**SYNTHETIC / RESEARCH_ONLY. All company, portfolio, instrument and outcome values are fictional. No capital should be deployed from this example.**

## Investment-relevant observation
The example decomposes a measured financed-emissions change into financed-amount, reported-issuer-emissions and EVIC effects. The three effects sum to the total change, with the residual shown explicitly.

## Reproduce the arithmetic
From the repository root:
```bash
python -m sf_agent calc --operation financed_emissions --arguments examples/calculation-arguments.json
```

### Inputs
```json
{
  "outstanding_amount": 1000000,
  "evic": 100000000,
  "emissions_tco2e": 500000
}
```

### Recomputed result
```json
5000.0
```

## What the result does not establish
Neither a reduction caused by sales nor an increase in EVIC proves real-world decarbonisation. Reconcile entry/exit, coverage and boundary effects with the portfolio helper. The inventory calculation uses bond book exposure and separate market-value weights for WACI; unknown data remain unassessed.

## Diligence handoff
Fictional corporate portfolio: a decline in measured financed emissions can arise from selling assets, changing EVIC or gaining data coverage, not just issuer decarbonisation.

Register source-backed inputs, contrary evidence, material data gaps and the investment constraints before replacing this illustrative result with actual research. Unit, boundary, timing, attribution and legal judgments are not supplied by arithmetic alone. No human research approval is recorded for this example.
