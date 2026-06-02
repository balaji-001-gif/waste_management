import frappe
from frappe.model.document import Document
from frappe.utils import flt

class WasteZone(Document):
    def validate(self):
        self.validate_coordinates()
        self.validate_collection_days()

    def validate_coordinates(self):
        if self.latitude and (flt(self.latitude) < -90 or flt(self.latitude) > 90):
            frappe.throw("Latitude must be between -90 and 90")
        if self.longitude and (flt(self.longitude) < -180 or flt(self.longitude) > 180):
            frappe.throw("Longitude must be between -180 and 180")

    def validate_collection_days(self):
        if self.collection_days:
            valid_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            days = [d.strip() for d in self.collection_days.split(",")]
            for day in days:
                if day not in valid_days:
                    frappe.throw(f"Invalid day: {day}. Use: Mon, Tue, Wed, Thu, Fri, Sat, Sun")

    @frappe.whitelist()
    def get_zone_statistics(self):
        stats = frappe.db.sql("""
            SELECT
                COUNT(wcr.name) as total_requests,
                SUM(wcr.actual_weight_kg) as total_weight,
                AVG(wcr.actual_weight_kg) as avg_weight
            FROM `tabWaste Collection Request` wcr
            WHERE wcr.zone = %s
            AND wcr.docstatus = 1
        """, self.name, as_dict=True)
        return stats[0] if stats else {}
