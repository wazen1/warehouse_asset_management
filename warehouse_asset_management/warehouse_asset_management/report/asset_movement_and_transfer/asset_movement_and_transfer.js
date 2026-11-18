// Copyright (c) 2026, Solvronix and contributors
// For license information, please see license.txt

frappe.query_reports["Asset Movement and Transfer"] = {
	"filters": [
		{
			"fieldname": "parent",
			"label": __("سجل الأصل"),
			"fieldtype": "Link",
			"options": "Asset Inventory"
		},
		{
			"fieldname": "action_type",
			"label": __("نوع الحركة"),
			"fieldtype": "Select",
			"options": "\nاستلام\nنقل بين المخازن\nتسليم للموظف\nإرجاع للمخزن\nربط بأصل ثابت"
		},
		{
			"fieldname": "warehouse",
			"label": __("المخزن"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname": "employee",
			"label": __("الموظف"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname": "from_date",
			"label": __("من تاريخ"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("إلى تاريخ"),
			"fieldtype": "Date"
		}
	]
};
