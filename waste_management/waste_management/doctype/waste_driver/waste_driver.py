import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, today

class WasteDriver(Document):
    def validate(self):
        self.check_license_expiry()
        self.update_performance_rating()

    def check_license_expiry(self):
        if self.license_expiry:
            days_to_expiry = date_diff(self.license_expiry, today())
            if days_to_expiry < 0:
                frappe.throw(f"Driver license has expired! Please update license details.")
            elif days_to_expiry <= 30:
                frappe.msgprint(
                    f"Driver license expires in {days_to_expiry} days!",
                    alert=True,
                    indicator="orange"
                )

    def update_performance_rating(self):
        total = frappe.db.count(
            "Waste Collection Request",
            filters={"driver": self.name, "docstatus": 1}
        )
        self.total_collections = total

        completed = frappe.db.count(
            "Waste Collection Request",
            filters={
                "driver": self.name,
                "status": "Completed",
                "docstatus": 1
            }
        )
        if total > 0:
            self.rating = round((completed / total) * 5, 2)
        else:
            self.rating = 0.0
