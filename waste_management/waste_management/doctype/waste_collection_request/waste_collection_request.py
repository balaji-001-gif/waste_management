import frappe
from frappe.model.document import Document
from frappe.utils import today, now_datetime, flt
import json

class WasteCollectionRequest(Document):
    def validate(self):
        self.validate_dates()
        self.set_status()
        self.run_ai_analysis()

    def validate_dates(self):
        if self.scheduled_date and self.scheduled_date < today():
            if self.status not in ["Completed", "Cancelled"]:
                frappe.msgprint(
                    "Scheduled date is in the past.",
                    alert=True,
                    indicator="orange"
                )

    def set_status(self):
        if self.docstatus == 0:
            self.status = "Pending"

    def run_ai_analysis(self):
        try:
            from waste_management.waste_management.ai.waste_ai_engine import WasteAIEngine
            ai_engine = WasteAIEngine()
            suggestions = ai_engine.analyze_collection_request(self)
            if suggestions:
                self.ai_risk_score = suggestions.get("risk_score", 0)
                self.ai_estimated_time_min = suggestions.get("estimated_time_min", 0)
                if suggestions.get("suggested_vehicle"):
                    self.ai_suggested_vehicle = suggestions.get("suggested_vehicle")
                if suggestions.get("suggested_route"):
                    self.ai_suggested_route = suggestions.get("suggested_route")
        except Exception as e:
            frappe.log_error(f"AI Analysis Error: {str(e)}", "Waste AI Engine")

    def on_submit(self):
        self.status = "Assigned"
        self.update_vehicle_status()
        self.send_confirmation_notification()
        self.create_sales_invoice_if_needed()

    def on_cancel(self):
        self.status = "Cancelled"
        self.release_vehicle()

    def update_vehicle_status(self):
        if self.vehicle:
            frappe.db.set_value("Waste Vehicle", self.vehicle, "vehicle_status", "In Service")

    def release_vehicle(self):
        if self.vehicle:
            frappe.db.set_value("Waste Vehicle", self.vehicle, "vehicle_status", "Available")

    def send_confirmation_notification(self):
        if self.customer:
            customer_email = frappe.db.get_value("Customer", self.customer, "email_id")
            if customer_email:
                try:
                    frappe.sendmail(
                        recipients=[customer_email],
                        subject=f"Waste Collection Request Confirmed - {self.name}",
                        template="waste_collection_confirmation",
                        args={
                            "customer_name": self.customer_name,
                            "request_id": self.name,
                            "scheduled_date": self.scheduled_date,
                            "vehicle": self.vehicle,
                            "driver": self.driver,
                        }
                    )
                except Exception as e:
                    frappe.log_error(f"Notification Error: {str(e)}", "Waste Collection Request")

    def create_sales_invoice_if_needed(self):
        if self.billing_amount and self.customer:
            try:
                invoice = frappe.get_doc({
                    "doctype": "Sales Invoice",
                    "customer": self.customer,
                    "posting_date": today(),
                    "due_date": today(),
                    "items": [
                        {
                            "item_code": "WASTE-COLLECTION-SERVICE",
                            "description": f"Waste Collection Service - {self.name}",
                            "qty": 1,
                            "rate": self.billing_amount,
                        }
                    ],
                    "custom_waste_request": self.name,
                })
                invoice.insert(ignore_permissions=True)
                self.db_set("invoice", invoice.name)
                frappe.msgprint(f"Sales Invoice {invoice.name} created.", alert=True)
            except Exception as e:
                frappe.log_error(str(e), "Create Invoice Error")

    @frappe.whitelist()
    def complete_collection(self, actual_weight, completion_notes="", photo=None):
        self.actual_weight_kg = flt(actual_weight)
        self.completion_notes = completion_notes
        if photo:
            self.completion_photo = photo
        self.actual_collection_date = today()
        self.status = "Completed"
        self.save()

        if self.driver:
            frappe.db.set_value(
                "Waste Driver",
                self.driver,
                "driver_status",
                "Available"
            )

        return {"status": "success", "message": "Collection completed successfully"}


def has_permission(doc, ptype, user):
    if frappe.has_role("System Manager", user=user) or frappe.has_role("Waste Manager", user=user):
        return True
    if ptype == "read" and doc.customer:
        customer_user = frappe.db.get_value("Customer", doc.customer, "customer_primary_contact")
        if customer_user == user:
            return True
    return False


def on_submit(doc, method=None):
    """Module-level doc_event hook called on submit of Waste Collection Request."""
    doc.status = "Assigned"
    doc.update_vehicle_status()
    doc.send_confirmation_notification()
    doc.create_sales_invoice_if_needed()


def on_cancel(doc, method=None):
    """Module-level doc_event hook called on cancel of Waste Collection Request."""
    doc.status = "Cancelled"
    doc.release_vehicle()

