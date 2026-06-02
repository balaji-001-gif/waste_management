import frappe
from frappe.model.document import Document
from frappe.utils import today

class WasteComplaint(Document):
    def validate(self):
        self.validate_resolution()

    def validate_resolution(self):
        if self.status == "Resolved":
            if not self.resolution_notes:
                frappe.throw("Resolution Notes are required to resolve a complaint.")
            if not self.resolved_date:
                self.resolved_date = today()
        elif self.status in ["Open", "In Review"]:
            self.resolved_date = None

    def on_submit(self):
        # Notify user or escalation logic can go here
        pass
