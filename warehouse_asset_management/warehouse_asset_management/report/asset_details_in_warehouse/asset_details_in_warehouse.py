# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		{"label": _("رمز السجل"), "fieldname": "name", "fieldtype": "Link", "options": "Asset Inventory", "width": 160},
		{"label": _("كود الصنف"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": _("اسم الصنف"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("الرقم التسلسلي"), "fieldname": "serial_no", "fieldtype": "Data", "width": 140},
		{"label": _("المخزن"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
		{"label": _("الفرع"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("تكلفة الشراء"), "fieldname": "purchase_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("سند الاستلام"), "fieldname": "purchase_receipt", "fieldtype": "Link", "options": "Purchase Receipt", "width": 150},
		{"label": _("المورد"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 150},
		{"label": _("الحالة"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("الأصل الثابت"), "fieldname": "fixed_asset", "fieldtype": "Link", "options": "Asset", "width": 150},
	]

	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			name,
			item_code,
			item_name,
			serial_no,
			warehouse,
			branch,
			purchase_cost,
			purchase_receipt,
			supplier,
			status,
			fixed_asset
		FROM `tabAsset Inventory`
		WHERE {conditions}
		ORDER BY warehouse, name DESC
	""", filters, as_dict=1)

	chart = get_chart(data)

	return columns, data, None, chart


def get_chart(data):
	if not data:
		return None

	status_map = {}
	for row in data:
		status = row.get("status") or _("غير محدد")
		status_map[status] = status_map.get(status, 0) + 1

	labels = list(status_map.keys())
	values = [status_map[s] for s in labels]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("عدد الأصول"), "chartType": "bar", "values": values}],
		},
		"type": "pie",
	}


def get_conditions(filters):
	conds = ["1=1"]
	if filters.get("company"):
		conds.append("company = %(company)s")
	if filters.get("warehouse"):
		conds.append("warehouse = %(warehouse)s")
	if filters.get("status"):
		conds.append("status = %(status)s")
	if filters.get("item_code"):
		conds.append("item_code = %(item_code)s")
	return " AND ".join(conds)
