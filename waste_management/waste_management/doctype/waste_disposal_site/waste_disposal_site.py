import frappe
from frappe.model.document import Document
from frappe.utils import flt

class WasteDisposalSite(Document):
    def validate(self):
        self.calculate_capacity_percentage()
        self.validate_capacity()

    def calculate_capacity_percentage(self):
        if self.total_capacity_tons and self.current_capacity_used_tons:
            self.capacity_percentage = flt(
                (self.current_capacity_used_tons / self.total_capacity_tons) * 100, 2
            )
        else:
            self.capacity_percentage = 0

    def validate_capacity(self):
        if self.capacity_percentage >= 90:
            frappe.msgprint(
                f"⚠️ Disposal site {self.site_name} is at {self.capacity_percentage}% capacity!",
                alert=True,
                indicator="red"
            )
        elif self.capacity_percentage >= 75:
            frappe.msgprint(
                f"Disposal site {self.site_name} is at {self.capacity_percentage}% capacity.",
                alert=True,
                indicator="orange"
            )
