# Asset customizations moved out of erpnext/assets/doctype/asset/asset.py

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

import erpnext.assets.doctype.asset.asset as asset_module
from erpnext.assets.doctype.asset.asset import Asset


class CustomAsset(Asset):
	def validate_asset_finance_books(self, row):
		# Keep a residual value of 1 so the asset never depreciates to zero
		remaining_value = flt(self.net_purchase_amount) - flt(self.opening_accumulated_depreciation)
		if (
			flt(row.expected_value_after_useful_life) == 0
			and self.calculate_depreciation
			and flt(remaining_value) > 1
		):
			row.expected_value_after_useful_life = 1

		super().validate_asset_finance_books(row)

	def validate_depreciation_start_date(self, row):
		# Default the start date to Available-for-use Date instead of throwing
		if not row.depreciation_start_date or getdate(row.depreciation_start_date) < getdate(
			self.available_for_use_date
		):
			row.depreciation_start_date = self.available_for_use_date

		if getdate(row.depreciation_start_date) < getdate(self.purchase_date):
			frappe.throw(_("Row #{0}: Next Depreciation Date cannot be before Purchase Date").format(row.idx))


@frappe.whitelist()
def get_item_details(item_code, asset_category, net_purchase_amount):
	"""Same as erpnext's, but prefers the category's Expected Value After Useful Life when set."""
	asset_category_doc = frappe.get_cached_doc("Asset Category", asset_category)
	books = []
	for d in asset_category_doc.finance_books:
		books.append(
			{
				"finance_book": d.finance_book,
				"depreciation_method": d.depreciation_method,
				"total_number_of_depreciations": d.total_number_of_depreciations,
				"frequency_of_depreciation": d.frequency_of_depreciation,
				"daily_prorata_based": d.daily_prorata_based,
				"shift_based": d.shift_based,
				"salvage_value_percentage": d.salvage_value_percentage,
				"expected_value_after_useful_life": d.expected_value_after_useful_life
				or flt(net_purchase_amount) * flt(d.salvage_value_percentage / 100),
				"depreciation_start_date": d.depreciation_start_date or nowdate(),
				"rate_of_depreciation": d.rate_of_depreciation,
			}
		)

	return books


# Asset.set_missing_values calls the module-level function directly
asset_module.get_item_details = get_item_details
