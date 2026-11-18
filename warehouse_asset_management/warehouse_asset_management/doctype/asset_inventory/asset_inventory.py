# Copyright (c) 2026, Solvronix and contributors
# For license information, please see license.txt

import io
import frappe
from frappe import _
from frappe.model.document import Document
import qrcode
import qrcode.image.svg


class AssetInventory(Document):
	def validate(self):
		self.validate_status_and_locations()

	def before_save(self):
		self.generate_qr_code()

	def validate_status_and_locations(self):
		# Enforce rule: cannot have employee without status being delivered
		if self.status == "مسلم للموظف" and not self.employee:
			frappe.throw(_("يجب تحديد الموظف عند التسليم"))

	def generate_qr_code(self):
		qr_data = (
			f"Asset ID: {self.name or ''}\n"
			f"Item: {self.item_code or ''} - {self.item_name or ''}\n"
			f"Serial No: {self.serial_no or ''}\n"
			f"Warehouse: {self.warehouse or ''}\n"
			f"Employee: {self.employee or ''}\n"
			f"Status: {self.status or ''}\n"
			f"Fixed Asset: {self.fixed_asset or ''}"
		)
		try:
			factory = qrcode.image.svg.SvgImage
			img = qrcode.make(qr_data, image_factory=factory)
			stream = io.BytesIO()
			img.save(stream)
			svg_xml = stream.getvalue().decode("utf-8")
			self.qr_code_html = f"""
				<div style="text-align: center; padding: 15px; background: var(--card-bg, #f8f9fa); border-radius: 8px; border: 1px solid var(--border-color, #e2e8f0);">
					<div style="width: 160px; height: 160px; margin: 0 auto;">
						{svg_xml}
					</div>
					<div style="margin-top: 10px; font-weight: bold; font-size: 13px; color: var(--text-color, #1e293b);">
						{self.name or ''}
					</div>
				</div>
			"""
		except Exception as e:
			frappe.log_error(f"Error generating QR code for {self.name}: {str(e)}")


@frappe.whitelist()
def transfer_asset(docname, to_warehouse, location=None, remarks=None):
	doc = frappe.get_doc("Asset Inventory", docname)

	# Rule 9: Prevent transferring asset not in warehouse
	if doc.status not in ["في المخزن", "تم إنشاء أصل ثابت"]:
		frappe.throw(
			_("لا يمكن نقل الأصل لأن حالته الحالية هي '{0}'. يلزم إرجاعه للمخزن أولاً.").format(doc.status)
		)

	if not to_warehouse:
		frappe.throw(_("يرجى تحديد المخزن المنقول إليه"))

	if doc.warehouse == to_warehouse:
		frappe.throw(_("المخزن المستهدف هو نفس المخزن الحالي"))

	from_wh = doc.warehouse

	# Log movement
	doc.append(
		"movement_logs",
		{
			"action_type": "نقل بين المخازن",
			"transaction_date": frappe.utils.now(),
			"from_warehouse": from_wh,
			"to_warehouse": to_warehouse,
			"location": location or doc.location,
			"user": frappe.session.user,
			"remarks": remarks or _("نقل الأصل بين المخازن"),
		},
	)

	# Update fields
	doc.db_set("warehouse", to_warehouse)
	if location:
		doc.db_set("location", location)

	# If status was in warehouse, maintain it
	if doc.status != "تم إنشاء أصل ثابت":
		doc.db_set("status", "في المخزن")

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc


@frappe.whitelist()
def deliver_to_employee(docname, employee, department=None, branch=None, location=None, delivery_date=None, remarks=None):
	doc = frappe.get_doc("Asset Inventory", docname)

	if doc.status == "مسلم للموظف":
		frappe.throw(_("الأصل مسلم لموظف بالفعل ({0}). يلزم إرجاعه أولاً.").format(doc.employee))

	if not employee:
		frappe.throw(_("يرجى تحديد الموظف المستلم"))

	# Log movement
	doc.append(
		"movement_logs",
		{
			"action_type": "تسليم للموظف",
			"transaction_date": delivery_date or frappe.utils.now(),
			"from_warehouse": doc.warehouse,
			"employee": employee,
			"department": department,
			"branch": branch,
			"location": location or doc.location,
			"user": frappe.session.user,
			"remarks": remarks or _("تسليم الأصل للموظف"),
		},
	)

	# Update fields
	doc.db_set("employee", employee)
	if department:
		doc.db_set("department", department)
	if branch:
		doc.db_set("branch", branch)
	if location:
		doc.db_set("location", location)

	doc.db_set("delivery_date", delivery_date or frappe.utils.nowdate())
	doc.db_set("status", "مسلم للموظف")

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc


@frappe.whitelist()
def return_to_warehouse(docname, to_warehouse, location=None, remarks=None):
	doc = frappe.get_doc("Asset Inventory", docname)

	if not to_warehouse:
		frappe.throw(_("يرجى تحديد المخزن الذي سيتم إرجاع الأصل إليه"))

	from_emp = doc.employee

	# Log movement
	doc.append(
		"movement_logs",
		{
			"action_type": "إرجاع للمخزن",
			"transaction_date": frappe.utils.now(),
			"from_warehouse": doc.warehouse,
			"to_warehouse": to_warehouse,
			"employee": from_emp,
			"location": location or doc.location,
			"user": frappe.session.user,
			"remarks": remarks or _("إرجاع الأصل إلى المخزن"),
		},
	)

	# Reset employee fields and update warehouse
	doc.db_set("employee", None)
	doc.db_set("department", None)
	doc.db_set("delivery_date", None)
	doc.db_set("warehouse", to_warehouse)
	if location:
		doc.db_set("location", location)

	if doc.fixed_asset:
		doc.db_set("status", "تم إنشاء أصل ثابت")
	else:
		doc.db_set("status", "في المخزن")

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc


@frappe.whitelist()
def link_fixed_asset(docname, fixed_asset_name):
	doc = frappe.get_doc("Asset Inventory", docname)
	if doc.fixed_asset and doc.fixed_asset == fixed_asset_name:
		return doc

	doc.db_set("fixed_asset", fixed_asset_name)
	if doc.status == "في المخزن":
		doc.db_set("status", "تم إنشاء أصل ثابت")

	doc.append(
		"movement_logs",
		{
			"action_type": "ربط بأصل ثابت",
			"transaction_date": frappe.utils.now(),
			"user": frappe.session.user,
			"remarks": _("تم ربط السجل مع Fixed Asset: {0}").format(fixed_asset_name),
		},
	)

	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc
