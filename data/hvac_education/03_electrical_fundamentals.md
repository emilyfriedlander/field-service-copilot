# Electrical Fundamentals for HVAC Technicians
*Source: HVAC Technician Training Series — Module 3*

## Ohm's Law & Basic Relationships

The three foundational quantities and their relationship:

```
V = I × R      (Voltage = Current × Resistance)
I = V / R      (Current = Voltage / Resistance)
R = V / I      (Resistance = Voltage / Current)
P = V × I      (Power in watts = Voltage × Current)
```

**Practical example:** A condenser fan motor rated 1.2A at 240V draws 288W.
If resistance across the motor winding reads 0Ω, it's shorted. If it reads OL (overload/infinite),
the winding is open.

---

## HVAC Electrical Systems Overview

### Voltage Classes in Residential/Light Commercial HVAC
- **24 VAC control circuit** — thermostat, contactor coil, control board signals, TXV solenoids
- **120 VAC** — some air handlers, indoor blower motors, heat strips (smaller), ECM power
- **240 VAC single-phase** — most residential condensing units, larger air handlers, heat strips
- **208/230/460 VAC 3-phase** — commercial equipment (rooftops, chillers, large compressors)

### The Control Circuit (24 VAC)
The 24 VAC circuit is derived from a **control transformer** (typically 40–75 VA) in the air
handler or furnace. It powers:
- Thermostat (R terminal = 24V hot, C terminal = common)
- Contactor coil (energizes to close the compressor/condenser fan circuit)
- Gas valve, reversing valve solenoid, humidifier, etc.

**Common 24V circuit problems:**
- Blown 3A fuse on the control board → always caused by a wiring short, not random failure
- C wire missing → thermostat battery drain, erratic smart thermostat operation
- Low transformer output (< 22V under load) → replace transformer

---

## Key HVAC Electrical Components

### Contactor
A relay that switches the high-voltage compressor and condenser fan circuit on/off using
the 24V control signal.

- **Testing:** With power off, check contact resistance — should be near 0Ω when closed
- **Pitting/burning:** Replace if contacts are pitted > 1mm or show burn marks
- **Stuck closed:** Compressor runs continuously; thermostat can't shut it off
- **Coil resistance:** Typical 24V contactor coil = 8–20Ω. Infinite = open coil; replace.
- **Single-pole vs. two-pole:** Always replace with same pole count and amperage rating

### Capacitors
Capacitors provide the phase shift needed to start single-phase motors (start capacitor)
and improve running efficiency (run capacitor).

- **Run capacitor:** Continuously in circuit. Measured in µF (microfarads). If weak or failed,
  motor will hum, run hot, draw high amperage, or not start.
- **Start capacitor:** Only in circuit during startup (< 1 second). Removed by a start relay
  or potential relay once motor reaches ~75% speed.
- **Dual-run capacitor:** One capacitor body with two sections — one for compressor, one for
  condenser fan motor. Common in residential units.

**Measuring capacitors:**
1. Disconnect power and discharge capacitor (short terminals through a 20kΩ resistor)
2. Remove wires, set meter to capacitance mode (µF)
3. Tolerance: ±6% of rated value. Example: 45µF capacitor — acceptable range: 42.3–47.7µF
4. A reading of 0, OL, or > 10% out of tolerance = replace

### Motors
**PSC (Permanent Split Capacitor) motor:** Standard single-phase induction motor used in
condenser fans and older blower motors. Requires a run capacitor.

**ECM (Electronically Commutated Motor):** DC brushless motor with integrated inverter.
More efficient, variable speed, used in modern blower motors and some condenser fans.
- ECM modules can be replaced separately from the motor in most Genteq/Regal Beloit designs
- Never apply DC voltage tests to ECM terminals; you will damage the module

**Testing a PSC motor (winding resistance):**
- Main winding to common: lower resistance (e.g., 3–8Ω)
- Start winding to common: higher resistance (e.g., 8–20Ω)
- Any winding reading 0Ω = shorted; OL = open; replace motor

---

## Reading Wiring Diagrams

### Diagram Types
- **Schematic (ladder) diagram:** Shows electrical function; components spread out logically.
  Best for troubleshooting logic.
- **Pictorial diagram:** Shows physical wire routing and component locations.
  Best for installation.

### Common Symbols
| Symbol          | Meaning                           |
|-----------------|-----------------------------------|
| NO              | Normally Open contact             |
| NC              | Normally Closed contact           |
| M               | Motor                             |
| CR              | Control relay                     |
| TS / TH         | Thermostat / Thermal limit        |
| HP / LP         | High-pressure / Low-pressure switch|
| ○—/—○           | Open switch                       |
| ○——○            | Closed switch                     |

### Troubleshooting with a Ladder Diagram
1. Identify the load (motor, contactor coil) that should be energized
2. Trace from L1 (hot) through every switch in series to the load and back to L2 (neutral/common)
3. Any open switch in the path that should be closed is your fault
4. Voltage test: measure across each component in the path — voltage across an open = fault found

---

## Safety: Electrical Lockout / Tagout

**LOTO procedure before opening any electrical panel:**
1. Notify affected personnel
2. Identify all energy sources (main disconnect, control transformer, capacitors)
3. Shut off all disconnects
4. Apply lockout device and personal lock
5. Test with non-contact tester — test the tester first on a known live source
6. Discharge capacitors through a 20kΩ resistor before touching
7. Verify de-energized before proceeding

**Never assume:** Always verify with a meter. Test voltage between L1–L2, L1–Ground, L2–Ground.

---

## Common Electrical Failure Patterns

| Symptom                        | Likely Cause                            | Test                              |
|--------------------------------|-----------------------------------------|-----------------------------------|
| Compressor hums, doesn't start | Weak/failed start or run capacitor      | Capacitance test                  |
| Unit trips breaker repeatedly  | Compressor locked rotor (LRA too high)  | Amp clamp on compressor leads     |
| 24V fuse blows immediately     | Shorted wire or solenoid coil           | Disconnect loads one at a time    |
| Condenser fan runs, compressor not | Open contactor, bad compressor terminals | Voltage at contactor output |
| Intermittent shutdown          | High-pressure switch opening, limit trips| Monitor pressures + temps under load|
