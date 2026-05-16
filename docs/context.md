# Sim1 Context (Short)

## Core Idea
Agent-based food economy. Prices and wages emerge from agent decisions.

## Layers
- Person: state + constraints + decisions (via Brain)
- Firm: container (owner, workers, wage_offer, cash, efficiency)
- Economy: coordinates markets and tick

## Person
- State: money, food, hunger, health, happiness, productivity
- Actions (via Brain): choose_role, choose_employment, choose_purchase
- Constraints: cannot overspend; buying clipped by money and supply
- Tick: consume → update hunger/health/happiness

## Firm
- State: owner, workers, wage_offer, cash, efficiency, health
- No strategy inside Firm
- Constraints: can_hire if wage_offer <= price and cash sufficient (may fund from owner)
- Production: (owner + workers productivity) * efficiency

## Brain (per Person)
- choose_role(person, economy)
- choose_employment(person, economy) -> Firm | None
- choose_purchase(person, economy) -> amount
- offer_wage(owner, firm, economy) -> float

## Markets
- Labor: firms publish wage_offer; workers pick best; firm enforces constraints
- Food: people buy based on hunger; spending distributed to firms by output share
- Price: damped update from (demand - supply)

## Tick
1. choose_roles
2. create_firms (seed with owner capital)
3. owners set wage_offer
4. match_labor (workers choose; firms accept)
5. produce → food_supply
6. pay_wages (from firm cash)
7. trading (people buy; revenue to firms)
8. firm profit/health; exit if unhealthy
9. person.tick()
10. update_price; record metrics

## Invariants
- Money conserved via transfers
- Food conserved in food_supply until consumed
- Brain proposes; Person/Firm enforce

## Next Focus
- reservation_wage (worker threshold)
- multiple brain types (personalities)
- firm bankruptcy signals / metrics
