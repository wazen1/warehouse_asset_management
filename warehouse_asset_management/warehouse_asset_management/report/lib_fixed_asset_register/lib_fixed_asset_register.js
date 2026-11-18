// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["LIB Fixed Asset Register"] = {
	onload: function(report) {
		// ── أزرار التنقل السريع لتقارير أصول المخازن ─────────────────
		report.page.add_inner_button(__('🏢 رصيد الأصول حسب المخزن'), function() {
			frappe.set_route('query-report', 'Asset Balance by Warehouse');
		}, __('تقارير أصول المخازن'));

		report.page.add_inner_button(__('📦 تفاصيل الأصول داخل المخازن'), function() {
			frappe.set_route('query-report', 'Asset Details in Warehouse');
		}, __('تقارير أصول المخازن'));

		report.page.add_inner_button(__('👤 الأصول المسلمة للموظفين'), function() {
			frappe.set_route('query-report', 'Assets Delivered to Employees');
		}, __('تقارير أصول المخازن'));

		report.page.add_inner_button(__('🔄 حركة ونقل الأصول'), function() {
			frappe.set_route('query-report', 'Asset Movement and Transfer');
		}, __('تقارير أصول المخازن'));

	},

	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nIn Location\nDisposed",
			default: "In Location",
		},
		{
			fieldname: "asset_category",
			label: __("Asset Category"),
			fieldtype: "Link",
			options: "Asset Category",
		},
		{
			fieldname: "plate_number_filter",
			label: __("رقم اللوحة"),
			fieldtype: "Data",
			depends_on: "eval:doc.asset_category && (doc.asset_category.indexOf('سيارات') >= 0 || doc.asset_category.indexOf('نقل') >= 0)",
		},
		{
			fieldname: "chassis_number_filter",
			label: __("رقم الهيكل"),
			fieldtype: "Data",
			depends_on: "eval:doc.asset_category && (doc.asset_category.indexOf('سيارات') >= 0 || doc.asset_category.indexOf('نقل') >= 0)",
		},
		{
			fieldname: "manufacture_year_filter",
			label: __("سنة الصنع"),
			fieldtype: "Int",
			depends_on: "eval:doc.asset_category && (doc.asset_category.indexOf('سيارات') >= 0 || doc.asset_category.indexOf('نقل') >= 0)",
		},
		{
			fieldname: "vehicle_color_filter",
			label: __("اللون"),
			fieldtype: "Data",
			depends_on: "eval:doc.asset_category && (doc.asset_category.indexOf('سيارات') >= 0 || doc.asset_category.indexOf('نقل') >= 0)",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: ["--Select a group--", "Asset Category", "Location"],
			default: "--Select a group--",
			reqd: 1,
		},
		{
			fieldname: "only_existing_assets",
			label: __("Only existing assets"),
			fieldtype: "Check",
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
		},
		{
			fieldname: "include_default_book_assets",
			label: __("Include Default FB Assets"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "filter_based_on",
			label: __("Period Based On"),
			fieldtype: "Select",
			options: ["--Select a period--", "Fiscal Year", "Date Range"],
			default: "--Select a period--",
		},
		{
			fieldname: "from_date",
			label: __("Start Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.nowdate(), -12),
			depends_on: "eval: doc.filter_based_on == 'Date Range'",
		},
		{
			fieldname: "to_date",
			label: __("End Date"),
			fieldtype: "Date",
			default: frappe.datetime.nowdate(),
			depends_on: "eval: doc.filter_based_on == 'Date Range'",
		},
		{
			fieldname: "from_fiscal_year",
			label: __("Start Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			depends_on: "eval: doc.filter_based_on == 'Fiscal Year'",
		},
		{
			fieldname: "to_fiscal_year",
			label: __("End Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			depends_on: "eval: doc.filter_based_on == 'Fiscal Year'",
		},
		{
			fieldname: "date_based_on",
			label: __("Date Based On"),
			fieldtype: "Select",
			options: ["Purchase Date", "Available For Use Date"],
			default: "Purchase Date",
			depends_on: "eval: doc.filter_based_on == 'Date Range' || doc.filter_based_on == 'Fiscal Year'",
		},
	],
};
