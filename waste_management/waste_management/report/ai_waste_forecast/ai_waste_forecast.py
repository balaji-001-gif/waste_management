import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Prediction Date", "fieldname": "prediction_date", "fieldtype": "Date", "width": 120},
        {"label": "Zone", "fieldname": "zone", "fieldtype": "Link", "options": "Waste Zone", "width": 120},
        {"label": "Category", "fieldname": "waste_category", "fieldtype": "Link", "options": "Waste Category", "width": 120},
        {"label": "Predicted Weight (kg)", "fieldname": "predicted_weight_kg", "fieldtype": "Float", "width": 150},
        {"label": "Actual Weight (kg)", "fieldname": "actual_weight_kg", "fieldtype": "Float", "width": 150},
        {"label": "Variance (kg)", "fieldname": "variance_kg", "fieldtype": "Float", "width": 120},
        {"label": "Accuracy (%)", "fieldname": "accuracy_percentage", "fieldtype": "Percent", "width": 120}
    ]

def get_data(filters):
    conditions = ""
    if filters and filters.get("zone"):
        conditions += " AND zone = %(zone)s"
    if filters and filters.get("from_date"):
        conditions += " AND prediction_date >= %(from_date)s"
    if filters and filters.get("to_date"):
        conditions += " AND prediction_date <= %(to_date)s"

    query = f"""
        SELECT
            prediction_date,
            zone,
            waste_category,
            predicted_weight_kg,
            actual_weight_kg,
            variance_kg,
            accuracy_percentage
        FROM `tabAI Waste Prediction`
        WHERE docstatus < 2 {conditions}
        ORDER BY prediction_date DESC
    """
    return frappe.db.sql(query, filters, as_dict=True)
