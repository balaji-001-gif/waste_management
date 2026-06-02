import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Zone", "fieldname": "zone", "fieldtype": "Link", "options": "Waste Zone", "width": 150},
        {"label": "Category", "fieldname": "waste_category", "fieldtype": "Link", "options": "Waste Category", "width": 150},
        {"label": "Total Requests", "fieldname": "total_requests", "fieldtype": "Int", "width": 120},
        {"label": "Completed Requests", "fieldname": "completed_requests", "fieldtype": "Int", "width": 150},
        {"label": "Total Weight (kg)", "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
        {"label": "Avg Weight (kg)", "fieldname": "avg_weight", "fieldtype": "Float", "width": 150}
    ]

def get_data(filters):
    conditions = ""
    if filters and filters.get("zone"):
        conditions += " AND zone = %(zone)s"
    if filters and filters.get("from_date"):
        conditions += " AND request_date >= %(from_date)s"
    if filters and filters.get("to_date"):
        conditions += " AND request_date <= %(to_date)s"

    query = f"""
        SELECT
            zone,
            waste_category,
            COUNT(name) as total_requests,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_requests,
            SUM(actual_weight_kg) as total_weight,
            AVG(actual_weight_kg) as avg_weight
        FROM `tabWaste Collection Request`
        WHERE docstatus < 2 {conditions}
        GROUP BY zone, waste_category
    """
    return frappe.db.sql(query, filters, as_dict=True)
