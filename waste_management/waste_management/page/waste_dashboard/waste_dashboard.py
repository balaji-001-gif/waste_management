import frappe
from frappe.utils import today, add_days

@frappe.whitelist()
def get_dashboard_data():
    # 1. Today's collections count
    today_collections = frappe.db.count("Waste Collection Request", filters={"request_date": today(), "docstatus": ["<", 2]})
    
    # 2. Active Fleet
    total_vehicles = frappe.db.count("Waste Vehicle")
    active_vehicles = frappe.db.count("Waste Vehicle", filters={"vehicle_status": "In Service"})
    
    # 3. Recycled Weight
    recycled_weight = frappe.db.sql("""
        SELECT SUM(r.actual_weight_kg)
        FROM `tabWaste Collection Request` r
        INNER JOIN `tabWaste Category` c ON r.waste_category = c.name
        WHERE r.status = 'Completed' AND c.waste_type = 'Recyclable' AND r.docstatus = 1
    """)[0][0] or 0.0
    
    # 4. Avg driver rating
    avg_driver_rating = frappe.db.sql("""
        SELECT AVG(rating) FROM `tabWaste Driver`
    """)[0][0] or 0.0
    
    # 5. Complaints
    pending_complaints = frappe.db.count("Waste Complaint", filters={"status": ["in", ["Open", "In Review"]]})
    
    # 6. Weight trends (last 7 days and future 3 days)
    trends = []
    for i in range(-7, 4):
        d = add_days(today(), i)
        actual = frappe.db.sql("""
            SELECT SUM(actual_weight_kg) FROM `tabWaste Collection Request`
            WHERE scheduled_date = %s AND status = 'Completed' AND docstatus = 1
        """, d)[0][0] or 0.0
        
        predicted = frappe.db.sql("""
            SELECT SUM(predicted_weight_kg) FROM `tabAI Waste Prediction`
            WHERE prediction_date = %s
        """, d)[0][0] or 0.0
        
        trends.append({
            "date": d,
            "actual": actual,
            "predicted": predicted
        })
        
    # 7. Category breakdown
    categories = frappe.db.sql("""
        SELECT r.waste_category, SUM(r.actual_weight_kg) as total_weight
        FROM `tabWaste Collection Request` r
        WHERE r.status = 'Completed' AND r.docstatus = 1
        GROUP BY r.waste_category
    """, as_dict=True)
    
    # 8. Landfills
    sites = frappe.db.get_all("Waste Disposal Site", 
                              filters={"is_active": 1}, 
                              fields=["name", "site_name", "site_type", "total_capacity_tons", "current_capacity_used_tons", "capacity_percentage"])
    
    # 9. Recent requests
    recent_requests = frappe.db.get_all("Waste Collection Request",
                                        filters={"docstatus": ["<", 2]},
                                        fields=["name", "zone", "waste_category", "priority", "ai_risk_score", "status"],
                                        order_by="creation desc",
                                        limit=7)
                                        
    return {
        "kpis": {
            "today_collections": today_collections,
            "active_fleet": f"{active_vehicles}/{total_vehicles}",
            "recycled_weight": f"{recycled_weight:,.1f}",
            "avg_driver_rating": round(avg_driver_rating, 2),
            "pending_complaints": pending_complaints
        },
        "trends": trends,
        "categories": categories,
        "sites": sites,
        "recent_requests": recent_requests
    }
