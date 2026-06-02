# waste_management/setup/install.py

import frappe

def after_install():
    """Seed default data for the Waste Management app after installation."""
    # Create default Waste Categories
    default_categories = [
        {"category_name": "Organic", "description": "Food waste, garden waste"},
        {"category_name": "Plastic", "description": "PET, HDPE, PVC, etc."},
        {"category_name": "Metal", "description": "Ferrous and non‑ferrous metals"},
        {"category_name": "Electronic", "description": "E‑waste and appliances"},
        {"category_name": "Hazardous", "description": "Chemicals, medical waste"},
    ]
    for cat in default_categories:
        if not frappe.db.exists("Waste Category", {"category_name": cat["category_name"]}):
            doc = frappe.get_doc({
                "doctype": "Waste Category",
                "category_name": cat["category_name"],
                "description": cat["description"]
            })
            doc.insert(ignore_permissions=True)

    # Create default Waste Zones
    default_zones = [
        {"zone_name": "North Zone", "description": "Northern part of the city"},
        {"zone_name": "South Zone", "description": "Southern part of the city"},
        {"zone_name": "East Zone", "description": "Eastern part of the city"},
        {"zone_name": "West Zone", "description": "Western part of the city"},
    ]
    for zone in default_zones:
        if not frappe.db.exists("Waste Zone", {"zone_name": zone["zone_name"]}):
            doc = frappe.get_doc({
                "doctype": "Waste Zone",
                "zone_name": zone["zone_name"],
                "description": zone["description"]
            })
            doc.insert(ignore_permissions=True)

    # Add custom fields to ERPNext standard DocTypes (Customer, Sales Invoice)
    custom_fields = {
        "Customer": [
            {
                "fieldname": "waste_customer_type",
                "label": "Customer Waste Type",
                "fieldtype": "Select",
                "options": "Residential\nCommercial\nIndustrial",
                "insert_after": "customer_group",
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "waste_invoice_flag",
                "label": "Waste Invoice",
                "fieldtype": "Check",
                "insert_after": "status",
            }
        ],
    }
    for doctype, fields in custom_fields.items():
        for field in fields:
            if not frappe.db.get_value("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
                frappe.get_doc({
                    "doctype": "Custom Field",
                    "dt": doctype,
                    "fieldname": field["fieldname"],
                    "label": field["label"],
                    "fieldtype": field["fieldtype"],
                    "options": field.get("options", ""),
                    "insert_after": field["insert_after"],
                }).insert(ignore_permissions=True)

    frappe.msgprint("🗑️ Waste Management default data installed successfully.")
