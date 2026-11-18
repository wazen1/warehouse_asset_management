# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def on_purchase_receipt_submit(doc, method=None):
	"""
	Auto-creates Asset Inventory record(s) when Purchase Receipt is submitted
	for items marked as Fixed Asset or Item Group Fixed Assets.
	"""
	for item in doc.items:
		item_doc = frappe.get_cached_doc("Item", item.item_code)

		is_fa = bool(item_doc.is_fixed_asset or getattr(item, "is_fixed_asset", 0))

		# We process items marked as Fixed Asset or configured for Asset Inventory tracking
		if is_fa:
			qty = int(item.qty or 1)
			serial_numbers = []
			if getattr(item, "serial_no", None):
				serial_numbers = [s.strip() for s in item.serial_no.split("\n") if s.strip()]

			for i in range(max(qty, len(serial_numbers))):
				serial_no = serial_numbers[i] if i < len(serial_numbers) else (item.serial_no if qty == 1 else None)
				wh = item.warehouse or doc.set_warehouse

				asset_inv = frappe.get_doc({
					"doctype": "Asset Inventory",
					"item_code": item.item_code,
					"item_name": item.item_name,
					"is_fixed_asset_item": 1,
					"serial_no": serial_no,
					"purchase_receipt": doc.name,
					"supplier": doc.supplier,
					"purchase_cost": item.rate or item.amount or 0,
					"company": doc.company,
					"warehouse": wh,
					"status": "في المخزن",
					"movement_logs": [
						{
							"action_type": "استلام",
							"transaction_date": frappe.utils.now(),
							"to_warehouse": wh,
							"user": frappe.session.user,
							"remarks": _("تم الاستلام بموجب سند الاستلام {0}").format(doc.name),
						}
					]
				})
				asset_inv.insert(ignore_permissions=True)
				frappe.msgprint(
					_("تم إنشاء سجل تخزين للأصل بنجاح: {0}").format(
						f"<a href='/app/asset-inventory/{asset_inv.name}'><b>{asset_inv.name}</b></a>"
					),
					alert=True,
				)


def on_asset_submit_or_update(doc, method=None):
	"""
	Links ERPNext standard Fixed Asset with pre-existing Asset Inventory.
	Ensures requirement 5 & 6 compliance without touching GL or Depreciation.
	"""
	asset_inv_name = getattr(doc, "custom_asset_inventory", None)

	if not asset_inv_name:
		filters = {"item_code": doc.item_code}
		if getattr(doc, "serial_no", None):
			filters["serial_no"] = doc.serial_no
		elif getattr(doc, "purchase_receipt", None):
			filters["purchase_receipt"] = doc.purchase_receipt

		match = frappe.db.get_value("Asset Inventory", filters, "name")
		if match:
			asset_inv_name = match
			doc.db_set("custom_asset_inventory", match)

	if asset_inv_name and frappe.db.exists("Asset Inventory", asset_inv_name):
		inv_doc = frappe.get_doc("Asset Inventory", asset_inv_name)
		if inv_doc.fixed_asset != doc.name:
			inv_doc.db_set("fixed_asset", doc.name)
			if inv_doc.status == "في المخزن":
				inv_doc.db_set("status", "تم إنشاء أصل ثابت")

			inv_doc.append(
				"movement_logs",
				{
					"action_type": "ربط بأصل ثابت",
					"transaction_date": frappe.utils.now(),
					"user": frappe.session.user,
					"remarks": _("تم الربط مع Fixed Asset: {0}").format(doc.name),
				},
			)
			inv_doc.save(ignore_permissions=True)
