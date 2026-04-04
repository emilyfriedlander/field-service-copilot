# HVAC Troubleshooting Field Guide
*Source: HVAC Technician Training Series — Module 5*

## The Diagnostic Method

Resist the urge to replace parts based on symptoms alone. Follow a structured diagnostic
process every time:

1. **Gather information** — talk to the customer; when did it start? Any changes? Strange noises?
2. **Observe before touching** — look at the equipment running (or attempting to run)
3. **Measure, don't assume** — get pressures, temperatures, voltages, amperages
4. **Narrow the cause** — use your measurements to confirm or rule out each hypothesis
5. **Verify the fix** — after the repair, confirm the system is operating within spec

---

## No-Cool Diagnostic Tree

```
System not cooling
├── Compressor not running
│   ├── No 24V at contactor coil → check thermostat, control board, safety switches
│   ├── 24V at coil but contactor not pulling in → replace contactor
│   ├── Contactor closed but compressor not running
│   │   ├── Check voltage at compressor terminals (L1-L2)
│   │   ├── Low voltage (< 208V on 230V circuit) → check disconnect, wiring
│   │   └── Good voltage, no start → capacitor test → locked rotor test → replace compressor
│   └── Compressor starts, trips on thermal overload repeatedly → high head pressure? check condenser
└── Compressor running, poor cooling
    ├── Check delta-T (supply vs. return)
    ├── Delta-T < 14°F
    │   ├── Check airflow (filter, blower, static pressure)
    │   ├── Check suction pressure
    │   │   ├── Very low (< 80 psi R-410A) → check superheat → low charge or restricted TXV
    │   │   └── Normal/high pressure, poor cooling → dirty evaporator coil? check CFM
    │   └── Evaporator frozen → shut down, find root cause (airflow or charge)
    └── Delta-T normal but room not cooling → load issue (windows open? excess people? solar gain?)
```

---

## No-Heat Diagnostic Tree (Gas Furnace)

```
Furnace not heating
├── No call for heat from thermostat → check thermostat wiring, W terminal
├── Inducer motor not starting
│   ├── Check 24V at inducer relay → control board issue
│   └── 24V present, not running → inducer motor failure
├── Inducer running, no ignition
│   ├── Check pressure switch (proves inducer) → measure pressure switch voltage
│   ├── Pressure switch not closing → check inducer suction, condensate drain, tubing
│   ├── Pressure switch closes → check igniter (should glow orange within 15–30 sec)
│   ├── Igniter glowing → check gas valve (24V at valve? valve opening? gas supply on?)
│   └── Gas ignites, then shuts off after few seconds → flame sensor dirty or failed
└── Furnace lights, runs, then shuts off on limit
    ├── Check static pressure (high static → high temp rise → limit trips)
    ├── Check airflow: filter, blower speed, supply/return balance
    └── Cracked heat exchanger? (CO risk — red-tag unit, do not operate)
```

---

## Heat Pump Specific: Not Heating in Winter

Heat pumps lose capacity as outdoor temperature drops. At the **balance point** (~30–35°F for
most residential units), the heat pump output equals the home's heat loss and supplemental
heat isn't needed. Below that, aux/emergency heat supplements.

**Reversing valve issues:**
- Stuck in cooling mode → system blows cold in heat mode
  - Test: measure suction and discharge line temps; suction should be warm in heat mode
  - Apply or remove 24V to reversing valve coil per wiring diagram to test
- Stuck in heating mode → system heats in cooling mode (rare, happens in summer)

**Defrost issues:**
- Ice buildup on outdoor coil is normal in cold/humid weather; defrost cycle should clear it
- Defrost board fault codes: consult manufacturer literature
- If ice never melts: check defrost thermostat, defrost board, reversing valve coil

---

## Furnace Fault Codes

Modern furnace control boards flash an LED fault code when they lock out. Always check the
sight glass or observation window for the LED before doing anything else.

| Flashes | Common Meaning (varies by brand) |
|---------|----------------------------------|
| 1       | System lockout (too many retries) — reset required |
| 2       | Pressure switch stuck open       |
| 3       | Pressure switch stuck closed     |
| 4       | Open high limit or rollout switch |
| 5       | Flame sense fault (no flame detected) |
| 6       | Low flame signal / dirty flame sensor |
| 7       | Gas valve fault                  |

*Always consult the specific manufacturer's fault code chart — codes vary by brand and model.*

To clear a lockout: cycle 24V power (disconnect thermostat R wire for 30 seconds, reconnect).
If it locks out again immediately, the fault is still present.

---

## Refrigerant Leak Detection Procedure

1. **Connect gauges** and note operating pressures
2. **Electronic leak detector:** Start at the lowest point (refrigerant is heavier than air);
   move slowly (1 in/sec) along joints, valves, flare connections, and coil circuits
3. **UV dye:** If no leak found electronically and a prior tech added dye, use UV lamp in
   dark conditions. Look for yellow-green staining.
4. **Nitrogen pressure test:** For empty systems or to pinpoint after shutdown.
   - Pressurize to 150–300 psi with nitrogen
   - Apply soap solution to all joints
   - Never use oxygen or compressed air — explosion risk
5. **Document:** Note exact leak location in the work order before repairing

**After repair:** Pressure-test with nitrogen, pull a vacuum to < 300 microns (target 250
microns), verify vacuum holds for 15 minutes (no rise = no leak), then charge system.

---

## Vacuum & Charging Procedure

### Evacuation
1. Isolate refrigerant with gauge manifold valves (recover first if refrigerant present)
2. Connect vacuum pump to high and low side
3. Pull vacuum below 300 microns — target 250 microns
4. Isolate pump (close manifold valves) and monitor for 15 minutes
   - Rising toward atmospheric pressure → leak
   - Rising slowly then leveling off → moisture present; re-evacuate
   - Holding below 500 microns → system is tight and dry

### Charging (R-410A)
- **Vapor charge (low-side, system running):** Used for trimming charge; charge until target
  superheat is reached (8–12°F for TXV, 10–18°F for fixed orifice)
- **Liquid charge (liquid line, system off):** Always charge R-410A as a liquid from the
  cylinder to prevent fractionation; use a liquid-only valve or meter the valve carefully
- Use manufacturer's charging chart — never guess based on pressures alone

---

## Customer Communication on Common Findings

| Finding                      | What to Tell the Customer                           |
|------------------------------|-----------------------------------------------------|
| Refrigerant leak found       | "The system has a leak at [location]. We need to repair the leak, test, evacuate, and recharge. Running it without repair wastes refrigerant and can damage the compressor." |
| Capacitor failed             | "The run capacitor has failed — it's like the battery that helps the motor start and run efficiently. This is one of the most common wear items." |
| Dirty evaporator coil        | "The indoor coil is heavily fouled. This restricts airflow and can cause freeze-up. A coil cleaning will restore full capacity." |
| Heat exchanger cracked        | "A cracked heat exchanger is a carbon monoxide risk. I have to red-tag the furnace — it cannot operate safely. This requires replacement of the heat exchanger or the furnace." |
| Oversized equipment (new install)| "Your current unit is oversized for your home. The right-sized unit will dehumidify better and last longer." |
