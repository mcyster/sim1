# Sim1 Economy Overview

## Goal

Simulate a food-based economy with many agents where prices, wages, production, and welfare emerge from agent decisions.

Key outputs over time:
- food production and inventory
- food price
- wages (firm wage offers)
- employment (workers + owners)
- health, happiness, hunger
- money/wealth distribution

## Architecture

Three layers with clear responsibilities:

- Person: state + constraints + decisions (via Brain)
- Firm: production container + constraints (no strategy)
- Economy: coordinates markets and interactions

Brains (per person) provide strategy:
- choose_role
- choose_employment
- choose_purchase
- offer_wage (for owners)

## Person

State:
- money, food, hunger, health, happiness, productivity
- role (Worker | Owner), employed flag, firm reference

Constraints (enforced in Person methods):
- cannot spend more money than available
- buying limited by price and market supply
- consumption reduces food and updates hunger

Lifecycle:
- `tick(economy)` updates consumption, hunger, health, happiness

## Firm

State:
- owner (Person)
- workers (list[Person])
- wage_offer (float)
- cash, efficiency, health

Constraints:
- can_hire only if wage_offer <= food_price and sufficient cash
- hiring may require owner to transfer funds to firm

Behavior:
- no internal strategy; owner brain sets wage_offer

Production:
- output = (owner + workers productivity) * efficiency
- efficiency decreases with worker count (coordination cost)

## Economy

State:
- people, firms
- food_price
- food_supply (inventory)

Responsibilities:
- create firms for owners (seeded with owner capital)
- set wages via owner brains
- match labor (workers choose firms; firms enforce constraints)
- run production and add to food_supply
- run market: people buy food; spending becomes firm revenue
- update prices based on supply vs demand

## Markets

### Labor Market
- Firms publish a single `wage_offer`
- Workers choose the best offer via their brain
- Firms accept via constraints (cash + profitability)

### Goods Market (Food)
- People request purchases based on hunger
- Actual purchases are clipped by affordability and supply
- Total spending is distributed to firms proportional to output

### Price Update
- Price adjusts with damped response to (demand - supply)

## Tick (Daily)

1. People decide roles (owner/worker)
2. Firms are created and seeded with owner capital
3. Owners set `wage_offer`
4. Workers choose employment; firms accept/reject
5. Firms produce food → added to `food_supply`
6. Wages paid from firm cash
7. People buy food → money flows to firms
8. Firm profit/loss applied; unhealthy firms exit
9. Each person runs `tick()` (consume, update health/happiness)
10. Price updated; metrics recorded

## Invariants

- Money is conserved except via transfers (wages, purchases)
- Food is conserved in `food_supply` until consumed
- Brains propose actions; Person/Firm enforce constraints

## Notes

- Single wage per firm per tick (no per-worker contracts yet)
- No credit/loans; growth requires owner capital
- Designed for multiple brain types (personalities / AI agents)
