# Fixed Asset Register with vehicle details (plate, chassis, year, colour).
# Builds on erpnext's Fixed Asset Register instead of copying it.

import frappe
from frappe import _

from erpnext.assets.report.fixed_asset_register import fixed_asset_register as base

VEHICLE_FIELDS = ("plate_number", "chassis_number", "manufacture_year", "vehicle_color")
VEHICLE_FILTERS = (
	"plate_number_filter",
	"chassis_number_filter",
	"manufacture_year_filter",
	"vehicle_color_filter",
)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns, data, message, chart = base.execute(filters)

	if filters.get("group_by") in ("Asset Category", "Location"):
		return columns, data, message, chart

	vehicle_map = get_vehicle_map(filters, [d.get("asset_id") for d in data])
	if any(filters.get(f) for f in VEHICLE_FILTERS):
		data = [d for d in data if d.get("asset_id") in vehicle_map]
		chart = base.prepare_chart_data(data, filters)

	for d in data:
		d.update(vehicle_map.get(d.get("asset_id"), {}))

	if is_vehicle_report(filters):
		columns.extend(get_vehicle_columns())

	return columns, data, message, chart


def get_vehicle_map(filters, asset_ids):
	if not asset_ids:
		return {}

	conditions = {"name": ["in", asset_ids]}
	if filters.get("plate_number_filter"):
		conditions["plate_number"] = ["like", f"%{filters.plate_number_filter}%"]
	if filters.get("chassis_number_filter"):
		conditions["chassis_number"] = ["like", f"%{filters.chassis_number_filter}%"]
	if filters.get("manufacture_year_filter"):
		conditions["manufacture_year"] = filters.manufacture_year_filter
	if filters.get("vehicle_color_filter"):
		conditions["vehicle_color"] = ["like", f"%{filters.vehicle_color_filter}%"]

	rows = frappe.get_all("Asset", filters=conditions, fields=["name", *VEHICLE_FIELDS])
	return {r.pop("name"): r for r in rows}


def is_vehicle_report(filters):
	category = (filters.get("asset_category") or "").lower()
	return any(v in category for v in ["سيار", "نقل", "مركب", "vehicle", "car"]) or any(
		filters.get(f) for f in VEHICLE_FILTERS
	)


def get_vehicle_columns():
	return [
		{"label": _("رقم اللوحة"), "fieldname": "plate_number", "fieldtype": "Data", "width": 110},
		{"label": _("رقم الهيكل"), "fieldname": "chassis_number", "fieldtype": "Data", "width": 140},
		{"label": _("سنة الصنع"), "fieldname": "manufacture_year", "fieldtype": "Int", "width": 90},
		{"label": _("اللون"), "fieldname": "vehicle_color", "fieldtype": "Data", "width": 90},
	]
