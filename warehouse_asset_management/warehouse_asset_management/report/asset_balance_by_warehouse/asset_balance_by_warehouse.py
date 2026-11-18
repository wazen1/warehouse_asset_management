# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = [
		{"label": _("المخزن"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 180},
		{"label": _("كود الصنف"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("اسم الصنف"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
		{"label": _("إجمالي العدد"), "fieldname": "total_qty", "fieldtype": "Int", "width": 110},
		{"label": _("المتاح بالمخزن"), "fieldname": "in_stock_qty", "fieldtype": "Int", "width": 120},
		{"label": _("المسلم للموظفين"), "fieldname": "delivered_qty", "fieldtype": "Int", "width": 130},
		{"label": _("تم إنشاء أصل ثابت"), "fieldname": "fixed_asset_qty", "fieldtype": "Int", "width": 140},
		{"label": _("إجمالي التكلفة"), "fieldname": "total_value", "fieldtype": "Currency", "width": 140},
	]

	conditions = get_conditions(filters)

	data = frappe.db.sql(f"""
		SELECT
			warehouse,
			item_code,
			item_name,
			COUNT(name) as total_qty,
			SUM(CASE WHEN status = 'في المخزن' THEN 1 ELSE 0 END) as in_stock_qty,
			SUM(CASE WHEN status = 'مسلم للموظف' THEN 1 ELSE 0 END) as delivered_qty,
			SUM(CASE WHEN fixed_asset IS NOT NULL AND fixed_asset != '' THEN 1 ELSE 0 END) as fixed_asset_qty,
			SUM(purchase_cost) as total_value
		FROM `tabAsset Inventory`
		WHERE {conditions}
		GROUP BY warehouse, item_code
		ORDER BY warehouse, item_code
	""", filters, as_dict=1)

	chart = get_chart(data)

	return columns, data, None, chart


def get_chart(data):
	if not data:
		return None

	warehouses = []
	warehouse_map = {}
	for row in data:
		wh = row.get("warehouse") or _("بدون مخزن")
		if wh not in warehouse_map:
			warehouse_map[wh] = {"in_stock": 0, "delivered": 0, "fixed_asset": 0}
		warehouse_map[wh]["in_stock"] += row.get("in_stock_qty") or 0
		warehouse_map[wh]["delivered"] += row.get("delivered_qty") or 0
		warehouse_map[wh]["fixed_asset"] += row.get("fixed_asset_qty") or 0

	warehouses = list(warehouse_map.keys())

	return {
		"data": {
			"labels": warehouses,
			"datasets": [
				{"name": _("المتاح بالمخزن"), "chartType": "bar", "values": [warehouse_map[wh]["in_stock"] for wh in warehouses]},
				{"name": _("المسلم للموظفين"), "chartType": "bar", "values": [warehouse_map[wh]["delivered"] for wh in warehouses]},
				{"name": _("تم إنشاء أصل ثابت"), "chartType": "bar", "values": [warehouse_map[wh]["fixed_asset"] for wh in warehouses]},
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
