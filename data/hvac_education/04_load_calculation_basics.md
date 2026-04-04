# Load Calculation Basics (ACCA Manual J Overview)
*Source: HVAC Technician Training Series — Module 4*

## Why Load Calculations Matter

Proper equipment sizing is the single biggest factor in long-term system performance and
customer satisfaction. Oversized equipment:
- Short-cycles (runs for short bursts), causing humidity problems and temperature swings
- Wears components faster (more starts = more wear)
- Wastes money — customer paid for capacity they can't use

Undersized equipment:
- Can't maintain setpoint on design days
- Runs continuously, driving up energy bills
- Shortens compressor life due to constant operation

**Rule of thumb sizing ("1 ton per 400–600 sq ft") is not acceptable for proper installations.**
Always use Manual J or approved software for new installs and replacements.

---

## Manual J: The Industry Standard

ACCA Manual J (8th Edition) is the ANSI-approved method for calculating residential heating
and cooling loads. Most jurisdictions require Manual J for permits.

### What Manual J Calculates
- **Cooling load** (in BTU/hr or tons): Heat that must be removed to maintain setpoint
- **Heating load** (in BTU/hr): Heat that must be added to maintain setpoint

These are calculated separately because the governing factors differ.

---

## Factors That Drive the Load

### Envelope (Building Shell)
- **Walls:** Construction type, insulation R-value, area
- **Roof/ceiling:** Insulation level, attic ventilation, roof color
- **Windows/doors:** U-factor (insulation), SHGC (solar heat gain coefficient), orientation
- **Floor/slab:** Insulation, ground contact area
- **Air infiltration:** Blower door test result or estimated ACH (air changes per hour)

### Internal & Solar Gains (Cooling Only)
- **Occupants:** ~250 BTU/hr sensible + 200 BTU/hr latent per person
- **Lighting:** Incandescent (~3.4 BTU/hr/W), LED (much lower)
- **Appliances:** Kitchen loads, electronics
- **Solar:** Window orientation and shading dramatically affect cooling load;
  west-facing unshaded windows are the worst offenders

### Design Conditions
- **Outdoor design temperature:** Use ASHRAE 99% heating / 1% cooling data for your location
  (not the record high/low — that would massively oversize the system)
- **Indoor setpoint:** Typically 70°F heating, 75°F cooling / 50% RH

### Example Design Temperatures (ASHRAE 1% Cooling / 99% Heating)
| City         | Cooling DB/WB    | Heating DB      |
|--------------|------------------|-----------------|
| Atlanta, GA  | 92°F / 74°F      | 22°F            |
| Austin, TX   | 99°F / 74°F      | 28°F            |
| Denver, CO   | 93°F / 60°F      | 1°F             |
| Phoenix, AZ  | 110°F / 71°F     | 34°F            |

*DB = dry bulb, WB = wet bulb*

---

## Sensible vs. Latent Load

Total cooling load = **sensible** + **latent**

- **Sensible load:** Dry heat (raises temperature). Removed by sensible cooling of the air.
- **Latent load:** Moisture (humidity). Removed by condensing water vapor on the evaporator coil.

**Sensible Heat Ratio (SHR):** The fraction of total load that is sensible.
- Typical residential: 0.70–0.80 (70–80% sensible)
- High-humidity climates (coastal, SE US): can be 0.65 or lower

Equipment SHR must be ≥ building SHR or the system won't control humidity even if it
maintains temperature. This is why some climates require two-stage or variable-speed equipment.

---

## Manual S: Equipment Selection

After calculating loads with Manual J, Manual S tells you how to select equipment.

Key rules:
- **Cooling:** Equipment capacity at design conditions must be within **100–115%** of calculated load
- **Heating:** Heat pump capacity can be up to 125% of load; gas furnace up to 140%
- Never select equipment based on nominal tonnage alone — use ARI/AHRI rated capacity at
  actual design conditions (temperature and airflow)
- An oversized furnace is usually less harmful than oversized cooling equipment

**Manufacturer expanded rating tables** show capacity at various outdoor temperatures and
indoor airflow rates. Always look up the actual capacity at your design conditions,
not the nominal rating on the nameplate.

---

## Duct System: Manual D

Duct sizing directly affects delivered capacity. A system with a correctly sized unit but
undersized ducts won't deliver rated airflow, reducing both capacity and efficiency.

### Target Airflow
- **Cooling:** 350–450 CFM per ton (400 CFM/ton is the standard design target)
- **Heating (gas):** 400 CFM per ton equivalent; 0.5–0.6 CFM/BTU/hr input

### Static Pressure
- Total External Static Pressure (TESP) must be within the equipment's rated range
- Residential air handlers: typically rated at 0.5 in. w.g. TESP
- Measure TESP at commissioning: sum of supply + return static pressure (excluding coil + filter)
- High static pressure = restricted airflow = poor performance and comfort

### Common Duct Problems
- Undersized return (most common residential issue) → high static, low airflow, short-cycling
- Long flex duct runs with sags → dramatically increases friction, reduces airflow
- Leaky duct connections → reduced delivery, potential pressure imbalance, air quality issues

---

## Field Verification at Commissioning

After installation, verify the system is actually delivering design performance:

1. **Measure TESP** with a magnehelic gauge or digital manometer
2. **Measure supply CFM** using a flow hood, anemometer grid, or temperature-rise method
3. **Record suction and liquid line pressures** and compare to manufacturer charging charts
4. **Measure delta-T** (supply vs. return): target 16–22°F for cooling
5. **Verify superheat and subcooling** within manufacturer spec
6. Document all readings on the startup form and leave a copy in the unit
