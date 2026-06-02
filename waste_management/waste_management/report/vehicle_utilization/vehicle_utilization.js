frappe.query_reports["Vehicle Utilization"] = {
	"filters": [
		{
			"fieldname": "status",
			"label": __("Vehicle Status"),
			"fieldtype": "Select",
			"options": "\nAvailable\nIn Service\nUnder Maintenance\nOut of Service"
		}
	]
};
