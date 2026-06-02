import frappe
from frappe.utils import flt, date_diff, today

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Zone Name", "fieldname": "zone_name", "fieldtype": "Link", "options": "Waste Zone", "width": 150},
        {"label": "Zone Type", "fieldname": "zone_type", "fieldtype": "Data", "width": 120},
        {"label": "Population", "fieldname": "population", "fieldtype": "Int", "width": 120},
        {"label": "Total Collected (kg)", "fieldname": "total_collected", "fieldtype": "Float", "width": 180},
        {"label": "Estimated Per Day (kg)", "fieldname": "estimated_per_day", "fieldtype": "Float", "width": 180},
        {"label": "Actual Per Day (kg)", "fieldname": "actual_per_day", "fieldtype": "Float", "width": 180},
        {"label": "Per Capita/Day (g)", "fieldname": "per_capita_g", "fieldtype": "Float", "width": 180}
    ]

def get_data(filters):
    conditions = ""
    date_range = 30
    if filters and filters.get("from_date") and filters.get("to_date"):
        date_range = max(1, date_diff(filters["to_date"], filters["from_date"]))

    zones_query = "SELECT name, zone_name, zone_type, population_estimate, estimated_waste_per_day_kg FROM `tabWaste Zone` WHERE 1=1"
    zones = frappe.db.sql(zones_query, as_dict=True)
    data = []

    for z in zones:
        request_conditions = " AND zone = %(zone)s"
        params = {"zone": z.name}
        if filters and filters.get("from_date"):
            request_conditions += " AND request_date >= %(from_date)s"
            params["from_date"] = filters["from_date"]
        if filters and filters.get("to_date"):
            request_conditions += " AND request_date <= %(to_date)s"
            params["to_date"] = filters["to_date"]

        metrics = frappe.db.sql(f"""
            SELECT SUM(actual_weight_kg) as total_weight
            FROM `tabWaste Collection Request`
            WHERE status = 'Completed' AND docstatus = 1 {request_conditions}
        """, params, as_dict=True)

        row = {
            "zone_name": z.name,
            "zone_type": z.zone_type,
            "population": z.population_estimate or 0,
            "total_collected": 0.0,
            "estimated_per_day": z.estimated_waste_per_day_kg or 0.0,
            "actual_per_day": 0.0,
            "per_capita_g": 0.0
        }

        if metrics and metrics[0].total_weight:
            total_weight = flt(metrics[0].total_weight)
            row["total_collected"] = total_weight
            row["actual_per_day"] = round(total_weight / date_range, 2)
            if z.population_estimate:
                row["per_capita_g"] = round((row["actual_per_day"] / z.population_estimate) * 1000.0, 2)

        data.append(row)
    return data
