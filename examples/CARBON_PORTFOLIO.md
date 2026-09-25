# Fictional portfolio inventory and attribution

One listed equity and one listed-company corporate bond demonstrate known versus unknown emissions and a coverage gain. All values are fictional; bond book exposure differs from market value.

```bash
python -m sf_agent calc --operation carbon_inventory --arguments examples/carbon-inventory-arguments.json
python -m sf_agent calc --operation portfolio_emissions_attribution --arguments examples/carbon-attribution-arguments.json
```

Inspect the JSON results alongside the methods. The example's unknown bond emissions must not be treated as a zero carbon footprint. No separate physical-decarbonisation claim or whole-portfolio emissions total is supported.
