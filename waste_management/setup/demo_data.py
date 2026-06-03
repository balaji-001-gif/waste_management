import frappe
from frappe.utils import today, add_days
import random

def generate_demo_data():
    """Generates 5 to 10 entries for all Waste Management doctypes."""
    frappe.flags.in_setup = True
    
    # 1. Waste Vehicles
    vehicles = [
        {"vehicle_number": "TN-01-AB-1234", "vehicle_type": "Compactor Truck", "capacity_kg": 5000, "vehicle_status": "Available", "next_service_date": add_days(today(), 30)},
        {"vehicle_number": "TN-02-XY-5678", "vehicle_type": "Tipper Truck", "capacity_kg": 3000, "vehicle_status": "Available", "next_service_date": add_days(today(), 15)},
        {"vehicle_number": "TN-03-LM-9012", "vehicle_type": "Mini Truck", "capacity_kg": 1500, "vehicle_status": "Available", "next_service_date": add_days(today(), 45)},
        {"vehicle_number": "TN-04-QR-3456", "vehicle_type": "Compactor Truck", "capacity_kg": 6000, "vehicle_status": "Available", "next_service_date": add_days(today(), 60)},
        {"vehicle_number": "TN-05-ST-7890", "vehicle_type": "Handcart", "capacity_kg": 8000, "vehicle_status": "Available", "next_service_date": add_days(today(), 10)},
        {"vehicle_number": "TN-06-UV-2345", "vehicle_type": "Tipper Truck", "capacity_kg": 4000, "vehicle_status": "In Service", "next_service_date": add_days(today(), -2)},
    ]
    for v in vehicles:
        if not frappe.db.exists("Waste Vehicle", {"vehicle_number": v["vehicle_number"]}):
            doc = frappe.get_doc({"doctype": "Waste Vehicle", **v})
            doc.insert(ignore_permissions=True)
            
    # 2. Waste Drivers
    drivers = [
        {"driver_name": "Ramesh Kumar", "license_number": "TN-LIC-1001", "phone": "9876543210", "driver_status": "Available", "license_expiry": add_days(today(), 365)},
        {"driver_name": "Suresh Singh", "license_number": "TN-LIC-1002", "phone": "9876543211", "driver_status": "Available", "license_expiry": add_days(today(), 365)},
        {"driver_name": "Murugan M", "license_number": "TN-LIC-1003", "phone": "9876543212", "driver_status": "Available", "license_expiry": add_days(today(), 365)},
        {"driver_name": "Abdul Rahman", "license_number": "TN-LIC-1004", "phone": "9876543213", "driver_status": "Available", "license_expiry": add_days(today(), 365)},
        {"driver_name": "John Doe", "license_number": "TN-LIC-1005", "phone": "9876543214", "driver_status": "On Leave", "license_expiry": add_days(today(), 365)},
    ]
    for d in drivers:
        if not frappe.db.exists("Waste Driver", {"license_number": d["license_number"]}):
            doc = frappe.get_doc({"doctype": "Waste Driver", **d})
            doc.insert(ignore_permissions=True)
            
    # 3. Waste Disposal Sites
    sites = [
        {"site_name": "Central Landfill", "location": "Perungudi", "capacity_tons": 50000},
        {"site_name": "North Processing Plant", "location": "Kodungaiyur", "capacity_tons": 45000},
        {"site_name": "Eco Recycling Center", "location": "Guindy", "capacity_tons": 10000},
        {"site_name": "South Composting Yard", "location": "Pallikaranai", "capacity_tons": 15000},
        {"site_name": "E-Waste Dismantling Unit", "location": "Ambattur", "capacity_tons": 5000},
    ]
    for s in sites:
        if not frappe.db.exists("Waste Disposal Site", {"site_name": s["site_name"]}):
            doc = frappe.get_doc({"doctype": "Waste Disposal Site", **s})
            doc.insert(ignore_permissions=True)
            
    # Get Master Data for Relations
    zones = frappe.get_all("Waste Zone", fields=["name", "zone_name"])
    categories = frappe.get_all("Waste Category", fields=["name"])
    all_vehicles = frappe.get_all("Waste Vehicle", fields=["name"])
    all_drivers = frappe.get_all("Waste Driver", fields=["name"])
    
    if not (zones and categories and all_vehicles and all_drivers):
        frappe.msgprint("Missing Master Data. Run setup first.")
        return
        
    # 4. Waste Routes
    routes = []
    for i in range(1, 6):
        z = random.choice(zones)
        route_name = f"{z['zone_name']} - Route {i}"
        if not frappe.db.exists("Waste Route", {"route_name": route_name}):
            doc = frappe.get_doc({
                "doctype": "Waste Route",
                "route_name": route_name,
                "zone": z["name"],
                "start_location": f"Start Point {i}",
                "end_location": f"End Point {i}",
                "waypoints": [
                    {"waypoint_name": f"Stop {i}-A"},
                    {"waypoint_name": f"Stop {i}-B"},
                    {"waypoint_name": f"Stop {i}-C"}
                ]
            })
            doc.insert(ignore_permissions=True)
            routes.append(doc.name)
            
    # 5. Waste Collection Schedules
    for i in range(1, 6):
        z = random.choice(zones)
        v = random.choice(all_vehicles)
        d = random.choice(all_drivers)
        doc = frappe.get_doc({
            "doctype": "Waste Collection Schedule",
            "zone": z["name"],
            "schedule_type": random.choice(["Daily", "Weekly"]),
            "start_date": today(),
            "end_date": add_days(today(), 30),
            "vehicle": v["name"],
            "driver": d["name"],
            "collection_time": "08:00:00",
            "waste_categories": [{"waste_category": c["name"]} for c in categories[:2]],
            "is_active": 1
        })
        try:
            doc.insert(ignore_permissions=True)
            doc.submit()
        except frappe.exceptions.ValidationError:
            pass # Skip if conflict
            
    # 6. Waste Collection Requests
    statuses = ["Pending", "Assigned", "In Progress", "Completed"]
    for i in range(1, 11):
        z = random.choice(zones)
        c = random.choice(categories)
        v = random.choice(all_vehicles)
        doc = frappe.get_doc({
            "doctype": "Waste Collection Request",
            "request_title": f"Demo Request {i}",
            "zone": z["name"],
            "waste_category": c["name"],
            "request_type": random.choice(["Ad-hoc", "Scheduled"]),
            "status": "Pending", # Starts pending
            "priority": random.choice(["Low", "Medium", "High"]),
            "scheduled_date": add_days(today(), random.randint(0, 5)),
            "pickup_address": f"Address {i}, {z['zone_name']}",
            "vehicle": v["name"],
        })
        doc.insert(ignore_permissions=True)
        if random.choice([True, False]):
            doc.submit()
            
    # 7. Waste Complaints
    for i in range(1, 8):
        z = random.choice(zones)
        doc = frappe.get_doc({
            "doctype": "Waste Complaint",
            "subject": f"Bin overflow at {z['zone_name']} location {i}",
            "description": "Waste has not been collected for two days.",
            "zone": z["name"],
            "status": random.choice(["Open", "In Progress", "Resolved"]),
            "priority": random.choice(["Medium", "High", "Critical"]),
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.msgprint("✨ Demo Data Generation Complete!")

