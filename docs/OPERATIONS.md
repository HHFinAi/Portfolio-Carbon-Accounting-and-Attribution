# Executable operation catalogue

Every operation requires supplied assumptions/provenance. No market or issuer data are inferred.

## `carbon_inventory`
```python
carbon_inventory(holdings: 'list[dict]', portfolio_market_value: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"holdings": "normalized_holding_records", "portfolio_market_value": "$money"}`. Output unit/type: `carbon_inventory`.

## `dscr`
```python
dscr(cash_available: 'float', debt_service: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"cash_available": "$money", "debt_service": "$money"}`. Output unit/type: `multiple`.

## `financed_emissions`
```python
financed_emissions(outstanding_amount: 'float', evic: 'float', emissions_tco2e: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"outstanding_amount": "$money", "evic": "$money", "emissions_tco2e": "tCO2e"}`. Output unit/type: `tCO2e`.

## `financed_emissions_bridge`
```python
financed_emissions_bridge(amount0: 'float', emissions0: 'float', evic0: 'float', amount1: 'float', emissions1: 'float', evic1: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"amount0": "$money", "emissions0": "tCO2e", "evic0": "$money", "amount1": "$money", "emissions1": "tCO2e", "evic1": "$money"}`. Output unit/type: `financed_emissions_bridge`.

## `holding_period_return`
```python
holding_period_return(initial_dirty_price: 'float', exit_dirty_price: 'float', cash_income: 'float', funding_cost: 'float', transaction_cost: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"initial_dirty_price": "$money", "exit_dirty_price": "$money", "cash_income": "$money", "funding_cost": "$money", "transaction_cost": "$money"}`. Output unit/type: `decimal_return`.

## `npv`
```python
npv(cashflows: 'list[float]', annual_discount: 'float') -> 'float'
```
Periodic NPV; cashflows[0] is at time zero, then annual periods.

Input units: `{"cashflows": "$money", "annual_discount": "decimal"}`. Output unit/type: `$money`.

## `portfolio_emissions_attribution`
```python
portfolio_emissions_attribution(previous_holdings: 'list[dict]', current_holdings: 'list[dict]', scope: 'str') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"previous_holdings": "normalized_holding_records", "current_holdings": "normalized_holding_records", "scope": "scope_name"}`. Output unit/type: `portfolio_emissions_attribution`.

## `scale`
```python
scale(value: 'float', factor: 'float') -> 'float'
```
Explicit arithmetic conversion; external unit semantics need human review.

Input units: `{"value": "$input_unit", "factor": "conversion_factor"}`. Output unit/type: `$output_unit`.
