import frappe
from frappe.model.document import Document

class WasteCategory(Document):
    def validate(self):
        self.validate_category_code()

    def validate_category_code(self):
        if self.category_code:
            self.category_code = self.category_code.upper().strip()

    def before_save(self):
        if not self.color_code:
            color_map = {
                "General": "#95a5a6",
                "Hazardous": "#e74c3c",
                "Recyclable": "#3498db",
                "Organic": "#2ecc71",
                "E-Waste": "#9b59b6",
                "Medical": "#e67e22",
                "Construction": "#f39c12",
            }
            self.color_code = color_map.get(self.waste_type, "#95a5a6")
