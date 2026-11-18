# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		{"label": _("رمز السجل"), "fieldname": "name", "fieldtype": "Link", "options": "Asset Inventory", "width": 160},
		{"label": _("الموظف"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 160},
		{"label": _("اسم الموظف"), "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
		{"label": _("القسم"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
		{"label": _("الفرع"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("الموقع"), "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 140},
		{"label": _("تاريخ التسليم"), "fieldname": "delivery_date", "fieldtype": "Date", "width": 130},
		{"label": _("كود الصنف"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": _("اسم الصنف"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("الرقم التسلسلي"), "fieldname": "serial_no", "fieldtype": "Data", "width": 140},
		{"label": _("المخزن الأصلي"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
		{"label": _("الأصل الثابت"), "fieldname": "fixed_asset", "fieldtype": "Link", "options": "Asset", "width": 150},
	]

	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			ai.name,
			ai.employee,
			emp.employee_name,
			ai.department,
			ai.branch,
			ai.location,
			ai.delivery_date,
			ai.item_code,
			ai.item_name,
			ai.serial_no,
			ai.warehouse,
			ai.fixed_asset
		FROM `tabAsset Inventory` ai
		LEFT JOIN `tabEmployee` emp ON ai.employee = emp.name
		WHERE {conditions}
		ORDER BY ai.delivery_date DESC, ai.employee
	""", filters, as_dict=1)

	chart = get_chart(data)

	return columns, data, None, chart


def get_chart(data):
	if not data:
		return None

	dept_map = {}
	for row in data:
		dept = row.get("department") or _("بدون قسم")
		dept_map[dept] = dept_map.get(dept, 0) + 1

	labels = list(dept_map.keys())
	values = [dept_map[d] for d in labels]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("عدد الأصول المسلمة"), "chartType": "bar", "values": values}],
		},
		"type": "bar",
	}


def get_conditions(filters):
	conds = ["ai.employee IS NOT NULL AND ai.employee != ''"]
	if filters.get("company"):
		conds.append("ai.company = %(company)s")
	if filters.get("employee"):
		conds.append("ai.employee = %(employee)s")
	if filters.get("department"):
		conds.append("ai.department = %(department)s")
	if filters.get("branch"):
		conds.append("ai.branch = %(branch)s")
	if filters.get("item_code"):
		conds.append("ai.item_code = %(item_code)s")
	return " AND ".join(conds)
