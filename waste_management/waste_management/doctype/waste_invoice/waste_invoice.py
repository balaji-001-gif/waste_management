import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, flt

class WasteInvoice(Document):
    def validate(self):
        self.calculate_amount()
        self.set_due_date()

    def calculate_amount(self):
        self.amount = flt(self.weight_kg or 0) * flt(self.rate_per_kg or 0)

    def set_due_date(self):
        if not self.due_date:
            self.due_date = add_days(self.billing_date or today(), 30)

    def on_submit(self):
        self.create_sales_invoice()
        self.status = "Unpaid"

    def on_cancel(self):
        if self.sales_invoice:
            try:
                # Cancel linked sales invoice if it is submitted
                si = frappe.get_doc("Sales Invoice", self.sales_invoice)
                if si.docstatus == 1:
                    si.cancel()
                elif si.docstatus == 0:
                    frappe.delete_doc("Sales Invoice", self.sales_invoice)
            except Exception as e:
                frappe.log_error(f"Cancel Invoice Error: {str(e)}", "Waste Invoice")
        self.status = "Cancelled"

    def create_sales_invoice(self):
        try:
            invoice = frappe.get_doc({
                "doctype": "Sales Invoice",
                "customer": self.customer,
                "posting_date": self.billing_date or today(),
                "due_date": self.due_date,
                "items": [
                    {
                        "item_code": "WASTE-COLLECTION-SERVICE",
                        "description": f"Waste Collection Service - Request ID: {self.collection_request}",
                        "qty": 1,
                        "rate": self.amount,
                    }
                ],
                "custom_waste_invoice": self.name
            })
            invoice.insert(ignore_permissions=True)
            invoice.submit()
            self.db_set("sales_invoice", invoice.name)
            frappe.msgprint(f"Associated Sales Invoice {invoice.name} created and submitted.", alert=True)
        except Exception as e:
            frappe.log_error(f"Invoicing Linkage Error: {str(e)}", "Waste Invoicing Linkage")
