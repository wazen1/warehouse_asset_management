// Copyright (c) 2026, Solvronix and contributors
// For license information, please see license.txt

frappe.query_reports["Assets Delivered to Employees"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("الشركة"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "employee",
			"label": __("الموظف"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "department",
			"label": __("القسم"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "branch",
			"label": __("الفرع"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "item_code",
			"label": __("الصنف"),
			"fieldtype": "Link",
			"options": "Item"
		}
	]
};
