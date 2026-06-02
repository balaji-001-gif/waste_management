import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Vehicle Number", "fieldname": "vehicle_number", "fieldtype": "Link", "options": "Waste Vehicle", "width": 150},
        {"label": "Vehicle Type", "fieldname": "vehicle_type", "fieldtype": "Data", "width": 150},
        {"label": "Vehicle Status", "fieldname": "vehicle_status", "fieldtype": "Data", "width": 120},
        {"label": "Capacity (kg)", "fieldname": "capacity_kg", "fieldtype": "Float", "width": 120},
        {"label": "Total Trips", "fieldname": "total_trips", "fieldtype": "Int", "width": 100},
        {"label": "Total Weight Carried (kg)", "fieldname": "total_weight", "fieldtype": "Float", "width": 180},
        {"label": "Avg Weight Per Trip (kg)", "fieldname": "avg_weight", "fieldtype": "Float", "width": 180},
        {"label": "Capacity Utilization (%)", "fieldname": "utilization", "fieldtype": "Percent", "width": 180}
    ]

def get_data(filters):
    vehicles_query = "SELECT name, vehicle_number, vehicle_type, vehicle_status, capacity_kg FROM `tabWaste Vehicle` WHERE 1=1"
    if filters and filters.get("status"):
        vehicles_query += " AND vehicle_status = %(status)s"
    
    vehicles = frappe.db.sql(vehicles_query, filters, as_dict=True)
    data = []

    for v in vehicles:
        metrics = frappe.db.sql("""
            SELECT
                COUNT(name) as total_trips,
                SUM(actual_weight_kg) as total_weight,
                AVG(actual_weight_kg) as avg_weight
            FROM `tabWaste Collection Request`
            WHERE vehicle = %s AND status = 'Completed' AND docstatus = 1
        """, v.name, as_dict=True)

        row = {
            "vehicle_number": v.vehicle_number,
            "vehicle_type": v.vehicle_type,
            "vehicle_status": v.vehicle_status,
            "capacity_kg": v.capacity_kg,
            "total_trips": 0,
            "total_weight": 0.0,
            "avg_weight": 0.0,
            "utilization": 0.0
        }

        if metrics and metrics[0].total_trips:
            m = metrics[0]
            row["total_trips"] = m.total_trips
            row["total_weight"] = flt(m.total_weight)
            row["avg_weight"] = flt(m.avg_weight)
            if v.capacity_kg:
                row["utilization"] = round((flt(m.avg_weight) / flt(v.capacity_kg)) * 100, 2)

        data.append(row)
    return data
