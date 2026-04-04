# Refrigeration Cycle Fundamentals
*Source: HVAC Technician Training Series — Module 1*

## The Vapor-Compression Refrigeration Cycle

All mechanical refrigeration systems work on the same principle: heat is absorbed in one
location (the evaporator) and rejected at another (the condenser) by repeatedly cycling a
refrigerant between liquid and vapor states.

### The Four Core Components

**1. Compressor**
The compressor is the heart of the system. It draws in low-pressure refrigerant vapor from
the evaporator and compresses it into a high-pressure, high-temperature vapor. This raises
the refrigerant's temperature above the outdoor ambient so heat can flow from the refrigerant
to the outdoor air.

- Types: reciprocating, scroll (most common in residential), screw (commercial), centrifugal
- The scroll compressor is dominant in residential equipment due to fewer moving parts,
  quieter operation, and higher efficiency
- Compressor failure is almost always a symptom, not a root cause — diagnose why before replacing

**2. Condenser**
High-pressure hot refrigerant vapor flows to the condenser coil. Outdoor air is blown across
the coil; the refrigerant gives up its heat and condenses into a high-pressure liquid.

- A dirty condenser coil is the #1 cause of high head pressure and compressor overload
- Clean the condenser coil at every maintenance visit — minimum annually
- Subcooling is measured at the condenser outlet; normal range: 10–20°F

**3. Metering Device (Expansion Valve or Orifice)**
The metering device creates the pressure drop that allows the high-pressure liquid refrigerant
to expand into a low-pressure, low-temperature mixture entering the evaporator.

- **TXV (Thermostatic Expansion Valve):** Self-regulating; maintains constant superheat.
  Better efficiency across varying load conditions. Requires a sensing bulb on the suction line.
- **Fixed orifice / piston:** Simpler, no moving parts, less expensive. Less efficient at
  part-load conditions. More sensitive to refrigerant charge.
- If a TXV is hunting (pressures swinging ±5 psi repeatedly), suspect a bad sensing bulb,
  incorrect refrigerant charge, or a plugged screen.

**4. Evaporator**
Low-pressure, low-temperature refrigerant enters the evaporator coil inside the air handler.
Warm indoor air is blown across the coil; the refrigerant absorbs heat and boils into a vapor.
This is where cooling (heat absorption) occurs.

- Evaporator coil freeze-up causes: low refrigerant charge, low airflow (dirty filter/blower),
  TXV failure, low outdoor temps
- Superheat is measured at the evaporator outlet; normal range: 8–12°F (TXV), 10–18°F (fixed orifice)

---

## Pressure-Temperature Relationship

Refrigerants change state at a fixed temperature for a given pressure. This is the
**pressure-temperature (P-T) relationship** and is the foundation of every HVAC diagnosis.

- Use a P-T chart (or the gauges' built-in scale) for your specific refrigerant
- **Saturation temperature** = the temperature at which the refrigerant changes state
  at the measured pressure
- Low suction pressure = low evaporator saturation temp = risk of freeze-up or insufficient cooling

### Common Refrigerants & Notes

| Refrigerant | Status          | Replaces  | Notes                                    |
|-------------|-----------------|-----------|------------------------------------------|
| R-22        | Phased out (EPA) | —         | No longer manufactured; recovery only   |
| R-410A      | Active           | R-22      | Higher pressures; requires separate tools|
| R-32        | Emerging         | R-410A    | Lower GWP; A2L (mildly flammable)       |
| R-454B      | Emerging         | R-410A    | EPA-approved lower-GWP replacement      |

---

## Key Diagnostic Measurements

| Measurement     | Where Taken              | Normal Range (R-410A, 95°F day) | What It Tells You |
|-----------------|--------------------------|----------------------------------|-------------------|
| Suction pressure| Low-side port            | 115–125 psi                      | Evaporator saturation; charge level |
| Head pressure   | High-side port           | 380–420 psi                      | Condenser efficiency; charge level  |
| Superheat       | Suction line (TXV system)| 8–12°F                           | Evaporator feed; charge (fixed ori.)|
| Subcooling      | Liquid line              | 10–20°F                          | Charge level; condenser performance |
| Delta-T (supply)| Supply vs. return air    | 16–22°F split                    | System capacity; airflow adequacy   |

**Golden rule:** Never add refrigerant based on pressure alone. Always measure superheat
and subcooling before adjusting charge.

---

## Common Refrigerant Cycle Problems

### Low Suction Pressure
**Possible causes:**
1. Low refrigerant charge (leak)
2. Restricted metering device (ice, debris, TXV failure)
3. Low airflow across evaporator (dirty filter, failed blower)
4. Closed or restricted suction line service valve

**Diagnostic path:** Check filter → measure airflow (delta-T) → measure superheat →
check for leaks → inspect TXV

### High Head Pressure
**Possible causes:**
1. Dirty/blocked condenser coil
2. Low airflow across condenser (failed condenser fan, recirculation)
3. Non-condensables in system (air, nitrogen)
4. Overcharge

**Diagnostic path:** Clean condenser coil → verify fan operation → measure subcooling →
check for non-condensables
