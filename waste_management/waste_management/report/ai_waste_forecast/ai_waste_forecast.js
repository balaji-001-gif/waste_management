frappe.query_reports["AI Waste Forecast"] = {
	"filters": [
		{
			"fieldname": "zone",
			"label": __("Waste Zone"),
			"fieldtype": "Link",
			"options": "Waste Zone"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
