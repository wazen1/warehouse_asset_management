# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		{"label": _("رمز السجل"), "fieldname": "parent", "fieldtype": "Link", "options": "Asset Inventory", "width": 160},
		{"label": _("نوع الحركة"), "fieldname": "action_type", "fieldtype": "Data", "width": 130},
		{"label": _("التاريخ والوقت"), "fieldname": "transaction_date", "fieldtype": "Datetime", "width": 150},
		{"label": _("كود الصنف"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": _("اسم الصنف"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("الرقم التسلسلي"), "fieldname": "serial_no", "fieldtype": "Data", "width": 130},
		{"label": _("من مخزن"), "fieldname": "from_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
		{"label": _("إلى مخزن"), "fieldname": "to_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
		{"label": _("الموظف المستلم"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
		{"label": _("الموقع"), "fieldname": "location", "fieldtype": "Link", "options": "Location", "width": 130},
		{"label": _("سند المخزون"), "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 140},
		{"label": _("المستخدم"), "fieldname": "user", "fieldtype": "Link", "options": "User", "width": 140},
		{"label": _("ملاحظات"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
	]

	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			aim.parent,
			aim.action_type,
			aim.transaction_date,
			ai.item_code,
			ai.item_name,
			ai.serial_no,
			aim.from_warehouse,
			aim.to_warehouse,
			aim.employee,
			aim.location,
			aim.stock_entry,
			aim.user,
			aim.remarks
		FROM `tabAsset Inventory Movement` aim
		INNER JOIN `tabAsset Inventory` ai ON aim.parent = ai.name
		WHERE {conditions}
		ORDER BY aim.transaction_date DESC, aim.creation DESC
	""", filters, as_dict=1)

	chart = get_chart(data)

	return columns, data, None, chart


def get_chart(data):
	if not data:
		return None

	action_map = {}
	for row in data:
		action = row.get("action_type") or _("غير محدد")
		action_map[action] = action_map.get(action, 0) + 1

	labels = list(action_map.keys())
	values = [action_map[a] for a in labels]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("عدد الحركات"), "chartType": "bar", "values": values}],
		},
		"type": "bar",
	}


def get_conditions(filters):
	conds = ["1=1"]
	if filters.get("parent"):
		conds.append("aim.parent = %(parent)s")
	if filters.get("action_type"):
		conds.append("aim.action_type = %(action_type)s")
	if filters.get("warehouse"):
		conds.append("(aim.from_warehouse = %(warehouse)s OR aim.to_warehouse = %(warehouse)s)")
	if filters.get("employee"):
		conds.append("aim.employee = %(employee)s")
	if filters.get("from_date"):
		conds.append("aim.transaction_date >= %(from_date)s")
	if filters.get("to_date"):
		conds.append("aim.transaction_date <= %(to_date)s")
	return " AND ".join(conds)
