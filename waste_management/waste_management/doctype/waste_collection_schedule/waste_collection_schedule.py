import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, getdate

class WasteCollectionSchedule(Document):
    def before_save(self):
        self.validate_driver_vehicle_availability()

    def validate_driver_vehicle_availability(self):
        if self.vehicle:
            conflicts = frappe.db.sql("""
                SELECT name FROM `tabWaste Collection Schedule`
                WHERE vehicle = %s
                AND name != %s
                AND is_active = 1
                AND docstatus = 1
                AND (
                    (start_date <= %s AND (end_date >= %s OR end_date IS NULL))
                )
            """, (self.vehicle, self.name or "New", self.start_date, self.start_date))

            if conflicts:
                frappe.msgprint(
                    f"Vehicle {self.vehicle} may have scheduling conflicts.",
                    alert=True,
                    indicator="orange"
                )

    def on_submit(self):
        self.generate_collection_requests()

    def generate_collection_requests(self):
        if self.schedule_type == "Daily":
            current_date = getdate(self.start_date)
            end = getdate(self.end_date) if self.end_date else add_days(current_date, 30)
            count = 0
            while current_date <= end and count < 60:
                self._create_request_for_date(current_date)
                current_date = add_days(current_date, 1)
                count += 1

        elif self.schedule_type == "Weekly":
            current_date = getdate(self.start_date)
            end = getdate(self.end_date) if self.end_date else add_days(current_date, 90)
            count = 0
            while current_date <= end and count < 13:
                self._create_request_for_date(current_date)
                current_date = add_days(current_date, 7)
                count += 1

    def _create_request_for_date(self, date):
        existing = frappe.db.exists("Waste Collection Request", {
            "zone": self.zone,
            "scheduled_date": str(date),
            "vehicle": self.vehicle,
            "request_type": "Scheduled",
        })
        if not existing:
            # Try to grab the first waste category from child table to satisfy validation
            waste_cat = "GENERAL"
            if hasattr(self, 'waste_categories') and self.waste_categories:
                waste_cat = self.waste_categories[0].waste_category
            else:
                # Let's try to query db for any active waste category
                cats = frappe.get_all("Waste Category", filters={"is_active": 1}, limit=1)
                if cats:
                    waste_cat = cats[0].name

            request = frappe.get_doc({
                "doctype": "Waste Collection Request",
                "request_title": f"Scheduled Collection - {self.zone} - {date}",
                "request_date": str(date),
                "scheduled_date": str(date),
                "scheduled_time": self.collection_time,
                "request_type": "Scheduled",
                "zone": self.zone,
                "vehicle": self.vehicle,
                "driver": self.driver,
                "status": "Pending",
                "priority": "Medium",
                "waste_category": waste_cat,
                "pickup_address": "Zone Area"
            })
            request.insert(ignore_permissions=True)

    @frappe.whitelist()
    def auto_generate_schedule():
        """Scheduled task"""
        active_schedules = frappe.get_all(
            "Waste Collection Schedule",
            filters={"is_active": 1, "docstatus": 1},
            fields=["name"]
        )
        for schedule in active_schedules:
            doc = frappe.get_doc("Waste Collection Schedule", schedule.name)
            tomorrow = add_days(today(), 1)
            doc._create_request_for_date(getdate(tomorrow))
