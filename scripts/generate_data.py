"""Generate synthetic HVAC field service jobs dataset (1,200 rows)."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# --- Constants ---
HVAC_JOB_TYPES = [
    "AC Tune-Up", "AC Repair", "AC Replacement",
    "Furnace Tune-Up", "Furnace Repair", "Furnace Replacement",
    "Heat Pump Installation", "Heat Pump Repair",
    "Mini-Split Installation", "Mini-Split Repair",
    "Duct Cleaning", "Duct Repair",
    "Thermostat Installation", "Refrigerant Recharge",
    "Blower Motor Replacement", "Evaporator Coil Cleaning",
    "Air Handler Replacement", "Zone Control Installation",
    "Indoor Air Quality Install", "Maintenance Agreement Visit",
]

INSTALLATION_TYPES = {
    "AC Replacement", "Furnace Replacement", "Heat Pump Installation",
    "Mini-Split Installation", "Air Handler Replacement",
    "Zone Control Installation", "Indoor Air Quality Install",
}

HVAC_EQUIPMENT = [
    "Carrier 2-Ton AC", "Carrier 3-Ton AC",
    "Lennox SLP98 Furnace", "Lennox XC21 AC",
    "Trane XR15 Heat Pump", "Trane S9X2 Furnace",
    "Goodman 2-Ton AC Unit", "Goodman GMVC96 Furnace",
    "Rheem RPRL Air Handler", "Rheem RGLG Furnace",
    "Bryant 288BNV Furnace", "Daikin 9k Mini-Split",
    "Mitsubishi MZ-GL09 Mini-Split", "York YCG 3-Ton AC",
    "Amana AMVC96 Furnace", "Heil H4A3 Heat Pump",
]

HVAC_ISSUES = [
    "Refrigerant leak", "Capacitor failure", "Dirty filter",
    "Frozen evaporator coil", "Faulty thermostat", "Blower motor failure",
    "Clogged condensate drain", "Cracked heat exchanger",
    "Failed contactor", "Dirty condenser coil", "Failed compressor",
    "Restricted airflow", "Short cycling", "No cooling / no heat",
    "Unusual noise or vibration", "High utility bills",
]

TECHNICIANS = [
    {"id": "TECH-001", "name": "Marcus Reyes",  "level": "Senior"},
    {"id": "TECH-002", "name": "Jordan Kim",    "level": "Mid"},
    {"id": "TECH-003", "name": "Priya Nair",    "level": "Junior"},
    {"id": "TECH-004", "name": "Devon Walsh",   "level": "Senior"},
    {"id": "TECH-005", "name": "Leila Okafor",  "level": "Mid"},
]

CITIES = [
    ("Austin", "TX"), ("Dallas", "TX"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Scottsdale", "AZ"), ("Tempe", "AZ"),
    ("Denver", "CO"), ("Aurora", "CO"), ("Lakewood", "CO"),
    ("Atlanta", "GA"), ("Marietta", "GA"), ("Alpharetta", "GA"),
]

STATUSES        = ["Completed", "Parts Ordered", "Pending Revisit",
                   "Incomplete", "On Hold", "Cancelled", "No Access", "Dispatched"]
STATUS_WEIGHTS  = [50, 12, 8, 7, 6, 5, 4, 8]

PRIORITY        = ["Low", "Medium", "Medium", "High", "Emergency"]
PRIORITY_WEIGHTS = [10, 40, 25, 15, 10]

CUSTOMER_TYPES  = ["Residential", "Residential", "Residential", "Commercial"]
PAYMENT_METHODS = ["Credit Card", "Credit Card", "Check", "Financing", "Cash"]
CALL_SOURCES    = ["Inbound Call", "Inbound Call", "Website", "Referral",
                   "Repeat Customer", "Google Ads"]


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def labor_hours(job_type: str, level: str) -> float:
    base = random.uniform(0.5, 4.0)
    if job_type in INSTALLATION_TYPES:
        base = random.uniform(3.0, 8.0)
    elif "Replacement" in job_type:
        base = random.uniform(2.0, 5.0)
    if level == "Junior":
        base *= random.uniform(1.1, 1.4)
    return round(base, 2)


def generate_row(job_id: int) -> dict:
    tech      = random.choice(TECHNICIANS)
    job_type  = random.choice(HVAC_JOB_TYPES)
    equipment = random.choice(HVAC_EQUIPMENT)
    issue     = random.choice(HVAC_ISSUES)
    city, state = random.choice(CITIES)

    sched_date  = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
    hours       = labor_hours(job_type, tech["level"])
    labor_rate  = {"Senior": 135, "Mid": 105, "Junior": 80}[tech["level"]]
    labor_cost  = round(hours * labor_rate, 2)

    # Installations and replacements have higher parts cost
    is_install  = job_type in INSTALLATION_TYPES
    parts_cost  = round(random.uniform(200, 3500), 2) if is_install else (
        round(random.uniform(20, 650), 2) if random.random() > 0.25 else 0.0
    )
    total_cost  = round(labor_cost + parts_cost, 2)

    status   = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    priority = random.choices(PRIORITY, weights=PRIORITY_WEIGHTS)[0]

    # First-time fix — seniors fix more often
    ftf_w = {"Senior": [82, 18], "Mid": [70, 30], "Junior": [52, 48]}[tech["level"]]
    first_time_fix = random.choices([True, False], weights=ftf_w)[0]

    csat = None
    if status == "Completed":
        if first_time_fix:
            csat = random.choices([3, 4, 5], weights=[8, 28, 64])[0]
        else:
            csat = random.choices([1, 2, 3, 4, 5], weights=[18, 22, 28, 22, 10])[0]

    # Membership conversion — offered on service/repair visits, not installations
    membership_offered   = status == "Completed" and job_type not in INSTALLATION_TYPES
    mem_conv_w = {"Senior": [35, 65], "Mid": [22, 78], "Junior": [12, 88]}[tech["level"]]
    membership_converted = membership_offered and random.choices([True, False], weights=mem_conv_w)[0]

    # System replacement opportunity — old-equipment repairs or tune-ups signal upsell
    replacement_opp_types = {"AC Repair", "AC Tune-Up", "Furnace Repair", "Furnace Tune-Up",
                             "Heat Pump Repair", "Refrigerant Recharge", "Maintenance Agreement Visit"}
    replacement_opportunity = job_type in replacement_opp_types and random.random() < 0.35
    rep_close_w = {"Senior": [45, 55], "Mid": [28, 72], "Junior": [12, 88]}[tech["level"]]
    replacement_sold = replacement_opportunity and random.choices([True, False], weights=rep_close_w)[0]

    call_source = random.choice(CALL_SOURCES)

    return {
        "job_id":                   f"JOB-{job_id:05d}",
        "scheduled_date":           sched_date.strftime("%Y-%m-%d"),
        "scheduled_time":           sched_date.strftime("%H:%M"),
        "trade":                    "HVAC",
        "job_type":                 job_type,
        "priority":                 priority,
        "status":                   status,
        "technician_id":            tech["id"],
        "technician_name":          tech["name"],
        "technician_level":         tech["level"],
        "customer_type":            random.choice(CUSTOMER_TYPES),
        "city":                     city,
        "state":                    state,
        "equipment_involved":       equipment,
        "reported_issue":           issue,
        "labor_hours":              hours,
        "labor_rate_usd":           labor_rate,
        "labor_cost_usd":           labor_cost,
        "parts_cost_usd":           parts_cost,
        "total_cost_usd":           total_cost,
        "payment_method":           random.choice(PAYMENT_METHODS),
        "first_time_fix":           first_time_fix,
        "csat_score":               csat if csat is not None else "",
        "revisit_required":         not first_time_fix and status == "Completed",
        "call_source":              call_source,
        "membership_offered":       membership_offered,
        "membership_converted":     membership_converted,
        "replacement_opportunity":  replacement_opportunity,
        "replacement_sold":         replacement_sold,
        "notes": (
            f"Tech noted: {random.choice(HVAC_ISSUES)}. "
            f"{'Parts ordered.' if parts_cost > 0 else 'No parts required.'}"
        ),
    }


def main():
    out_path = Path(__file__).parent.parent / "data" / "jobs.csv"
    rows = [generate_row(i + 1) for i in range(1200)]

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} rows → {out_path}")


if __name__ == "__main__":
    main()
