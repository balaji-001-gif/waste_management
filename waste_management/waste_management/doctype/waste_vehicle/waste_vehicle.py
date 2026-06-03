import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, date_diff

class WasteVehicle(Document):
    def validate(self):
        self.check_maintenance_alerts()
        self.check_document_expiry()

    def check_maintenance_alerts(self):
        if self.next_service_date:
            days_to_service = date_diff(self.next_service_date, today())
            if days_to_service <= 7 and days_to_service >= 0:
                frappe.msgprint(
                    f"Vehicle {self.vehicle_number} is due for service in {days_to_service} days!",
                    alert=True,
                    indicator="orange"
                )
            elif days_to_service < 0:
                frappe.msgprint(
                    f"Vehicle {self.vehicle_number} is OVERDUE for service!",
                    alert=True,
                    indicator="red"
                )

    def check_document_expiry(self):
        if self.insurance_expiry:
            days_to_expiry = date_diff(self.insurance_expiry, today())
            if days_to_expiry <= 30:
                frappe.msgprint(
                    f"Insurance for {self.vehicle_number} expires in {days_to_expiry} days!",
                    alert=True,
                    indicator="red"
                )

    @frappe.whitelist()
    def get_vehicle_location(self):
        return {
            "latitude": self.current_latitude,
            "longitude": self.current_longitude,
            "vehicle_number": self.vehicle_number,
            "status": self.vehicle_status
        }


def update_vehicle_status():
    """Module-level scheduled task to update vehicle status based on active collections."""
    vehicles = frappe.get_all(
        "Waste Vehicle",
        filters={"vehicle_status": "In Service"},
        fields=["name", "vehicle_number"]
    )
    for vehicle in vehicles:
        active_collections = frappe.db.count(
            "Waste Collection Request",
            filters={
                "vehicle": vehicle.name,
                "status": ["in", ["In Progress", "Assigned"]],
                "docstatus": 1
            }
        )
        if not active_collections:
            frappe.db.set_value("Waste Vehicle", vehicle.name, "vehicle_status", "Available")
    frappe.db.commit()
