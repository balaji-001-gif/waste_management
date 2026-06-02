import frappe
from frappe.utils import flt

class WasteAIEngine:
    def __init__(self):
        pass

    def analyze_collection_request(self, doc):
        """
        Analyzes a Waste Collection Request to determine:
        1. Risk score (probability of delays or handling errors)
        2. Estimated completion time (in minutes)
        3. Suggested vehicle
        4. Suggested route
        """
        suggestions = {
            "risk_score": 0.0,
            "estimated_time_min": 30,
            "suggested_vehicle": None,
            "suggested_route": ""
        }

        # 1. Calculate Risk Score
        # Heuristics: high priority increases risk, hazardous/medical waste increases risk,
        # and zone history of complaints increases risk.
        risk = 0.1
        if doc.priority == "High":
            risk += 0.2
        elif doc.priority == "Critical":
            risk += 0.4

        if doc.special_handling_required:
            risk += 0.3

        # Add risk if there are unresolved complaints in the zone
        if doc.zone:
            unresolved_complaints = frappe.db.count("Waste Complaint", filters={
                "zone": doc.zone,
                "status": ["in", ["Open", "In Review"]]
            })
            risk += min(0.3, unresolved_complaints * 0.1)

        suggestions["risk_score"] = min(1.0, risk)

        # 2. Calculate Estimated Time (min)
        # Base transit time = 25 minutes. Loading time = 2 minutes per bin or 0.1 min per kg.
        weight = flt(doc.estimated_weight_kg or 0.0)
        bins = flt(doc.number_of_bins or 1)
        loading_time = (bins * 2.0) + (weight * 0.05)
        suggestions["estimated_time_min"] = int(25.0 + loading_time)

        # 3. Suggest a Vehicle
        # Pick an available vehicle from the same zone whose capacity fits the waste weight.
        vehicles = frappe.get_all(
            "Waste Vehicle",
            filters={
                "vehicle_status": "Available",
                "assigned_zone": doc.zone or ""
            },
            fields=["name", "capacity_kg"],
            order_by="capacity_kg asc"
        )

        # Fallback to any available vehicle if zone-specific is not found
        if not vehicles:
            vehicles = frappe.get_all(
                "Waste Vehicle",
                filters={"vehicle_status": "Available"},
                fields=["name", "capacity_kg"],
                order_by="capacity_kg asc"
            )

        if vehicles:
            # Find the smallest vehicle that can handle the estimated weight
            suitable_vehicle = None
            for v in vehicles:
                if v.capacity_kg >= weight:
                    suitable_vehicle = v.name
                    break
            # If weight is too large, pick the vehicle with the largest capacity
            if not suitable_vehicle:
                suitable_vehicle = vehicles[-1].name
            suggestions["suggested_vehicle"] = suitable_vehicle

        # 4. Suggest a Route
        # Find active routes associated with this zone
        if doc.zone:
            routes = frappe.get_all(
                "Waste Route",
                filters={"zone": doc.zone, "is_active": 1},
                fields=["name", "route_name"],
                limit=1
            )
            if routes:
                suggestions["suggested_route"] = routes[0].name
            else:
                suggestions["suggested_route"] = f"Standard Route - Zone {doc.zone}"

        return suggestions
