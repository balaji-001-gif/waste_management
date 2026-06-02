import frappe
from frappe.model.document import Document

class WasteRoute(Document):
    def validate(self):
        self.validate_waypoints()

    def validate_waypoints(self):
        if self.route_waypoints:
            # Re-index waypoints sequentially to ensure order consistency
            waypoints_sorted = sorted(self.route_waypoints, key=lambda x: x.stop_number or 0)
            for idx, waypoint in enumerate(waypoints_sorted, 1):
                waypoint.stop_number = idx
