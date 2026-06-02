import frappe
from frappe.model.document import Document

class ScheduleWasteCategory(Document):
    """Controller for the child table *Schedule Waste Category*.
    This DocType is a simple child table linking a waste category to a schedule.
    No custom business logic is required, so the class is intentionally empty.
    """
    pass
