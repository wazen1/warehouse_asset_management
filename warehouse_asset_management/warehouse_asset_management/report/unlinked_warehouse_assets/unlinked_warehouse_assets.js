// Copyright (c) 2026, Solvronix and contributors
// For license information, please see license.txt

frappe.query_reports["Unlinked Warehouse Assets"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("الشركة"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "warehouse",
			"label": __("المخزن"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname": "item_code",
			"label": __("الصنف"),
			"fieldtype": "Link",
			"options": "Item"
		}
	]
};
