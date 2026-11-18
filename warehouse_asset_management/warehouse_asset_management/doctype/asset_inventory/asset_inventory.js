// Copyright (c) 2026, Solvronix and contributors
// For license information, please see license.txt

frappe.ui.form.on("Asset Inventory", {
	refresh(frm) {
		if (frm.is_new()) return;

		// Action: Transfer Asset ("نقل الأصل")
		if (frm.doc.status === "في المخزن" || frm.doc.status === "تم إنشاء أصل ثابت") {
			frm.add_custom_button(__("نقل الأصل"), () => {
				frappe.prompt(
					[
						{
							fieldname: "to_warehouse",
							fieldtype: "Link",
							options: "Warehouse",
							label: __("إلى مخزن"),
							reqd: 1
						},
						{
							fieldname: "location",
							fieldtype: "Link",
							options: "Location",
							label: __("الموقع (اختياري)"),
							default: frm.doc.location
						},
						{
							fieldname: "remarks",
							fieldtype: "Small Text",
							label: __("ملاحظات النقل")
						}
					],
					(values) => {
						frappe.call({
							method: "warehouse_asset_management.warehouse_asset_management.doctype.asset_inventory.asset_inventory.transfer_asset",
							args: {
								docname: frm.doc.name,
								to_warehouse: values.to_warehouse,
								location: values.location,
								remarks: values.remarks
							},
							freeze: true,
							freeze_message: __("جاري نقل الأصل..."),
							callback: (r) => {
								if (!r.exc) {
									frappe.show_alert({ message: __("تم نقل الأصل بنجاح"), indicator: "green" });
									frm.reload_doc();
								}
							}
						});
					},
					__("نقل الأصل بين المخازن"),
					__("تأكيد النقل")
				);
			}).addClass("btn-primary");
		}

		// Action: Deliver Asset ("تسليم الأصل")
		if (frm.doc.status !== "مسلم للموظف") {
			frm.add_custom_button(__("تسليم الأصل"), () => {
				frappe.prompt(
					[
						{
							fieldname: "employee",
							fieldtype: "Link",
							options: "Employee",
							label: __("الموظف المستلم"),
							reqd: 1
						},
						{
							fieldname: "department",
							fieldtype: "Link",
							options: "Department",
							label: __("القسم"),
							default: frm.doc.department
						},
						{
							fieldname: "branch",
							fieldtype: "Link",
							options: "Branch",
							label: __("الفرع"),
							default: frm.doc.branch
						},
						{
							fieldname: "location",
							fieldtype: "Link",
							options: "Location",
							label: __("الموقع"),
							default: frm.doc.location
						},
						{
							fieldname: "delivery_date",
							fieldtype: "Date",
							label: __("تاريخ التسليم"),
							default: frappe.datetime.get_today(),
							reqd: 1
						},
						{
							fieldname: "remarks",
							fieldtype: "Small Text",
							label: __("ملاحظات التسليم")
						}
					],
					(values) => {
						frappe.call({
							method: "warehouse_asset_management.warehouse_asset_management.doctype.asset_inventory.asset_inventory.deliver_to_employee",
							args: {
								docname: frm.doc.name,
								employee: values.employee,
								department: values.department,
								branch: values.branch,
								location: values.location,
								delivery_date: values.delivery_date,
								remarks: values.remarks
							},
							freeze: true,
							freeze_message: __("جاري تسجيل تسليم الأصل..."),
							callback: (r) => {
								if (!r.exc) {
									frappe.show_alert({ message: __("تم تسليم الأصل بنجاح"), indicator: "green" });
									frm.reload_doc();
								}
							}
						});
					},
					__("تسليم الأصل لموظف"),
					__("تأكيد التسليم")
				);
			}).addClass("btn-info");
		}

		// Action: Return to Warehouse ("إرجاع للمخزن")
		if (frm.doc.status === "مسلم للموظف") {
			frm.add_custom_button(__("إرجاع للمخزن"), () => {
				frappe.prompt(
					[
						{
							fieldname: "to_warehouse",
							fieldtype: "Link",
							options: "Warehouse",
							label: __("إلى مخزن"),
							default: frm.doc.warehouse,
							reqd: 1
						},
						{
							fieldname: "location",
							fieldtype: "Link",
							options: "Location",
							label: __("الموقع الجديد"),
							default: frm.doc.location
						},
						{
							fieldname: "remarks",
							fieldtype: "Small Text",
							label: __("ملاحظات الإرجاع")
						}
					],
					(values) => {
						frappe.call({
							method: "warehouse_asset_management.warehouse_asset_management.doctype.asset_inventory.asset_inventory.return_to_warehouse",
							args: {
								docname: frm.doc.name,
								to_warehouse: values.to_warehouse,
								location: values.location,
								remarks: values.remarks
							},
							freeze: true,
							freeze_message: __("جاري إرجاع الأصل للمخزن..."),
							callback: (r) => {
								if (!r.exc) {
									frappe.show_alert({ message: __("تم إرجاع الأصل إلى المخزن بنجاح"), indicator: "green" });
									frm.reload_doc();
								}
							}
						});
					},
					__("إرجاع الأصل للمخزن"),
					__("تأكيد الإرجاع")
				);
			});
		}

		// Action: Create Fixed Asset ("إنشاء Fixed Asset")
		if (!frm.doc.fixed_asset) {
			frm.add_custom_button(__("إنشاء Fixed Asset"), () => {
				frappe.model.with_doctype("Asset", () => {
					let new_asset = frappe.model.get_new_doc("Asset");
					new_asset.item_code = frm.doc.item_code;
					new_asset.asset_name = frm.doc.item_name;
					new_asset.purchase_receipt = frm.doc.purchase_receipt;
					new_asset.gross_purchase_amount = frm.doc.purchase_cost;
					new_asset.purchase_amount = frm.doc.purchase_cost;
					new_asset.company = frm.doc.company;
					new_asset.custom_asset_inventory = frm.doc.name;
					frappe.set_route("Form", "Asset", new_asset.name);
				});
			}, __("Actions"));
		}
	}
});
