# SpaceTrader Expansion Plan

## 1) Vision
- Build a terminal-first space sandbox inspired by TradeWars:
  - Explore sectors/systems
  - Trade for profit
  - Manage risk (pirates, hazards, scarcity)
  - Fight, flee, or negotiate
  - Build long-term faction reputation and player progression

## 2) Core Gameplay Loop
1. Scan area (short/long range)
2. Choose destination (risk vs reward)
3. Travel (time + fuel + random events)
4. Trade, mine, or mission interaction
5. Resolve danger (combat/evasion/diplomacy)
6. Upgrade ship and repeat

## 3) Feature Pillars

### A. Economy and Trading (High Priority)
- Market model per system:
  - Supply, demand, legality, taxes, embargoes
- Commodity classes:
  - Basics (food, ore, fuel), industrial, rare tech, contraband
- Price simulation:
  - Dynamic pricing based on local events and traffic
- NPC traders:
  - Compete with player, influence prices over time
- Cargo gameplay:
  - Capacity, perishables, smuggling risk, insurance

### B. Factions and NPCs (High Priority)
- Major factions with agendas:
  - Corporations, government patrols, pirates, miners, black market
- Reputation:
  - Influences docking rights, prices, mission access, hostility
- NPC captains:
  - Distinct behavior archetypes (aggressive, cautious, opportunist)
- Stations/ports:
  - Unique services and local political modifiers

### C. Danger and Survival (High Priority)
- Travel hazards:
  - Ion storms, asteroid fields, gravity anomalies, fuel leaks
- Encounter system:
  - Pirate interdictions, distressed ships, patrol inspections
- Risk controls:
  - Scan quality, stealth modules, route planning

### D. Combat and Tactical Outcomes (Medium-High Priority)
- Basic combat loop:
  - Range bands, weapon cooldown, shield/armor/hull layers
- Combat choices:
  - Attack, board, jam, retreat, surrender, call for aid
- Post-combat outcomes:
  - Loot, salvage, repairs, reputation effects, legal penalties

### E. Exploration and Progression (Medium Priority)
- Fog-of-war knowledge:
  - Discovered vs known by rumor
- Upgrades:
  - Engines, sensors, cargo, weapons, drone bays
- Crew system:
  - Officers with skills/perks (trade, combat, engineering)
- Win/loss framing:
  - Career score, debt pressure, permadeath optional mode

## 4) LLM Integration Opportunities

### Practical Uses (Start Here)
- Dynamic mission text:
  - Generate mission flavor from system/faction context
- NPC dialogue:
  - Personality-driven negotiation taunts and offers
- Event narration:
  - Better logs for hazards, discoveries, combat outcomes

### Advanced Uses
- AI market rumors:
  - “Insider tips” with uncertain reliability
- Faction newsfeed:
  - Periodic generated bulletins changing market sentiment
- Procedural contract generation:
  - Constraints from real game state, text by LLM

### Guardrails
- Keep game logic deterministic in code; use LLM for text and optional proposals only.
- Validate all LLM outputs against schema before use.
- Keep a non-LLM fallback mode for offline/local play.
- Cache generated text per event seed to avoid cost and inconsistency.

## 5) Suggested Data Model Additions
- `Commodity`: id, base_price, volatility, legality, mass
- `Market`: system_id, commodity_prices, stock, demand
- `Faction`: id, relations, territory, modifiers
- `NpcShip`: loadout, behavior_profile, cargo, allegiance
- `Encounter`: type, risk_rating, reward_rating, seed
- `Mission`: issuer, objectives, deadline, payout, penalties

## 6) Technical Plan (Phased)

### Phase 1: Economy MVP
- Add commodities + per-system markets
- Add buy/sell UI flow in viewport
- Add player wallet, cargo manifest, fuel costs
- Add save/load game state (JSON or sqlite)

### Phase 2: Travel Risk + Encounters
- Add encounter generator on travel completion
- Add hazard outcomes to stats/resources
- Add inspect/flee/engage choices

### Phase 3: Combat and AI
- Add turn-based combat resolution
- Add NPC ship archetypes and loot tables
- Add combat logs and repair loop

### Phase 4: Factions + Missions
- Reputation modifiers on trade/combat actions
- Mission board with faction-specific rewards
- Dynamic system control events

### Phase 5: LLM Enhancements
- Add narration + NPC dialogue provider abstraction
- Implement schema-validated text generation
- Add local/offline template fallback

## 7) UX and Interface Ideas
- Split viewport tabs:
  - `Cartography`, `Market`, `Comms`, `Contracts`, `Combat`
- Quick actions:
  - Keyboard-first prompts for buy/sell/flee/scan
- Better telemetry:
  - Fuel ETA, route risk score, legal heat meter
- Visual feedback:
  - Keep ASCII map style, add color semantics consistently

## 8) Balancing Targets
- Trading profit should be steady but risk-limited.
- Combat should be dangerous; retreat should stay viable.
- Smuggling should offer high reward with real legal downside.
- Scanning intelligence should materially reduce ambush risk.

## 9) Immediate Next Sprint (Concrete)
1. Implement commodities + market UI.
2. Add wallet/cargo/fuel tracking to ship stats.
3. Add travel encounter roll with simple outcomes.
4. Add first hostile NPC encounter (pirate) with minimal combat choice.
5. Add save/load to persist progression.

## 10) Open Design Questions
- Is the game single-captain roguelike or long campaign?
- How punishing should failure be (insurance, permadeath, debt)?
- How simulation-heavy should markets be vs gamey and readable?
- Should LLM be optional flavor or also drive mission structure?
