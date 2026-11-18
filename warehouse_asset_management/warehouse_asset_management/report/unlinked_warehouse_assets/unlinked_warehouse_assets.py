# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		{"label": _("كود الصنف"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": _("اسم الصنف"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		{"label": _("المخزن"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
		{"label": _("الفرع"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("الكمية الإجمالية"), "fieldname": "total_qty", "fieldtype": "Int", "width": 120},
		{"label": _("الرصيد الحالي"), "fieldname": "current_balance", "fieldtype": "Int", "width": 120},
		{"label": _("الرصيد المسحوب"), "fieldname": "withdrawn_qty", "fieldtype": "Int", "width": 120},
		{"label": _("تكلفة الشراء الإجمالية"), "fieldname": "total_purchase_cost", "fieldtype": "Currency", "width": 140},
	]

	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			item_code,
			item_name,
			warehouse,
			branch,
			COUNT(*) AS total_qty,
			SUM(CASE WHEN fixed_asset IS NULL OR fixed_asset = '' THEN 1 ELSE 0 END) AS current_balance,
			SUM(CASE WHEN fixed_asset IS NOT NULL AND fixed_asset <> '' THEN 1 ELSE 0 END) AS withdrawn_qty,
			SUM(purchase_cost) AS total_purchase_cost
		FROM `tabAsset Inventory`
		WHERE {conditions}
		GROUP BY item_code, warehouse
		ORDER BY warehouse, item_code
	""", filters, as_dict=1)

	chart = get_chart(data)

	return columns, data, None, chart


def get_chart(data):
	if not data:
		return None

	warehouse_map = {}
	for row in data:
		wh = row.get("warehouse") or _("بدون مخزن")
		if wh not in warehouse_map:
			warehouse_map[wh] = {"current": 0, "withdrawn": 0}
		warehouse_map[wh]["current"] += row.get("current_balance") or 0
		warehouse_map[wh]["withdrawn"] += row.get("withdrawn_qty") or 0

	warehouses = list(warehouse_map.keys())

	return {
		"data": {
			"labels": warehouses,
			"datasets": [
				{"name": _("الرصيد الحالي"), "chartType": "bar", "values": [warehouse_map[wh]["current"] for wh in warehouses]},
				{"name": _("الرصيد المسحوب"), "chartType": "bar", "values": [warehouse_map[wh]["withdrawn"] for wh in warehouses]},
			],
		},
		"type": "bar",
	}


def get_conditions(filters):
	conds = ["1=1"]
	if filters.get("company"):
		conds.append("company = %(company)s")
	if filters.get("warehouse"):
		conds.append("warehouse = %(warehouse)s")
	if filters.get("item_code"):
		conds.append("item_code = %(item_code)s")
	return " AND ".join(conds)
