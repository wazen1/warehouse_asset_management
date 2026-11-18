// Asset form customizations (moved out of erpnext/assets/doctype/asset/asset.js)

function wam_fix_depreciation_start_dates(frm) {
	if (!frm.doc.available_for_use_date || !frm.doc.finance_books) return;
	frm.doc.finance_books.forEach((d) => {
		if (
			!d.depreciation_start_date ||
			frappe.datetime.get_diff(d.depreciation_start_date, frm.doc.available_for_use_date) < 0
		) {
			frappe.model.set_value(d.doctype, d.name, "depreciation_start_date", frm.doc.available_for_use_date);
		}
	});
}

function wam_can_fetch_finance_books(frm) {
	return frm.doc.item_code && frm.doc.calculate_depreciation && frm.doc.net_purchase_amount;
}

frappe.ui.form.on("Asset", {
	validate: function (frm) {
		wam_fix_depreciation_start_dates(frm);
	},

	available_for_use_date: function (frm) {
		wam_fix_depreciation_start_dates(frm);
	},

	asset_type: function (frm) {
		frm.trigger("toggle_reference_doc");
	},

	asset_category: function (frm) {
		if (wam_can_fetch_finance_books(frm)) {
			frm.trigger("set_finance_book");
		}
	},

	net_purchase_amount: function (frm) {
		if (wam_can_fetch_finance_books(frm) && !(frm.doc.finance_books || []).length) {
			frm.trigger("set_finance_book");
		}
	},
});
