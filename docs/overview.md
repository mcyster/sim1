# Sim1 Economy Spec

## Goal

Simulate a simple food-based economy with thousands of people.

The simulation should show basic economic dynamics over time:

- food production
- food supply and demand
- food price changes
- employment
- health
- happiness
- wealth distribution

## Core Concepts

## Person

Each person has:

- money
- food
- happiness
- health
- productivity
- employed

### Money

Money is used to buy food.

### Food

Food is stored by a person and consumed each tick.

### Happiness

Happiness represents morale and general satisfaction.

Happiness affects employment probability.

### Health

Health represents physical condition.

Health decreases when a person cannot eat.

Health may affect happiness and employment probability.

### Productivity

Productivity controls how much food a person produces when employed.

### Employed

Employed means the person works during the current tick.

## Food

Food is the only produced good.

Food is:

- produced by employed people
- bought by people
- eaten by people
- priced based on supply and demand

## Simulation Tick

Each tick represents one day.

For each tick:

1. Each person becomes employed or unemployed for the tick.
2. Employed people produce food based on productivity.
3. Employed people earn money.
4. Economy calculates food supply.
5. Economy calculates food demand.
6. Food price increases or decreases based on supply and demand.
7. People buy food if they can afford it.
8. People eat food if they have it.
9. Health is updated.
10. Happiness is updated.
11. Metrics are recorded.
12. Graphs are updated.

## Employment

Each person may be employed or unemployed each tick.

Employment probability may be based on happiness and health.

Example:

```text
employment_probability = happiness * health / 10000
```

