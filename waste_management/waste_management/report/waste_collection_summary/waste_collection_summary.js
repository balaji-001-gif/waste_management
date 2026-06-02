frappe.query_reports["Waste Collection Summary"] = {
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
