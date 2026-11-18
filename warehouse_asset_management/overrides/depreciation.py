# Optional manual approval of scheduled depreciation entries.
# When "Require Depreciation Entry Approval" is enabled in Accounts Settings, scheduled
# depreciation creates draft Journal Entries instead of submitting them. Submitting the
# draft later links it to its schedule row through erpnext's own Journal Entry.on_submit.

import inspect

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate

import erpnext.assets.doctype.asset.depreciation as depr_module

_original = depr_module._make_journal_entry_for_depreciation
_EXPECTED_PARAMS = [
	"depr_schedule_doc",
	"asset",
	"date",
	"depr_schedule",
	"sch_start_idx",
	"sch_end_idx",
	"depr_cost_center",
	"depr_series",
	"credit_account",
	"debit_account",
	"accounting_dimensions",
]


def approval_required():
	return cint(frappe.db.get_single_value("Accounts Settings", "require_depreciation_entry_approval"))


def _draft_exists(asset, depr_schedule_doc, depr_schedule):
	je = frappe.qb.DocType("Journal Entry")
	jea = frappe.qb.DocType("Journal Entry Account")
	query = (
		frappe.qb.from_(je)
		.join(jea)
		.on(jea.parent == je.name)
		.select(je.name)
		.where(
			(je.docstatus == 0)
			& (je.voucher_type == "Depreciation Entry")
			& (je.posting_date == depr_schedule.schedule_date)
			& (jea.reference_type == "Asset")
			& (jea.reference_name == asset.name)
		)
		.limit(1)
	)
	if depr_schedule_doc.finance_book:
		query = query.where(je.finance_book == depr_schedule_doc.finance_book)
	return bool(query.run())


def make_journal_entry_for_depreciation(
	depr_schedule_doc,
	asset,
	date,
	depr_schedule,
	sch_start_idx,
	sch_end_idx,
	depr_cost_center,
	depr_series,
	credit_account,
	debit_account,
	accounting_dimensions,
):
	args = (
		depr_schedule_doc,
		asset,
		date,
		depr_schedule,
		sch_start_idx,
		sch_end_idx,
		depr_cost_center,
		depr_series,
		credit_account,
		debit_account,
		accounting_dimensions,
	)
	if not approval_required():
		return _original(*args)

	if not (sch_start_idx and sch_end_idx) and not (
		not depr_schedule.journal_entry and getdate(depr_schedule.schedule_date) <= getdate(date)
	):
		return
	if _draft_exists(asset, depr_schedule_doc, depr_schedule):
		return

	# Same as erpnext, but the entry is left as draft for review instead of being submitted
	je = frappe.new_doc("Journal Entry")
	depr_module.setup_journal_entry_metadata(je, depr_schedule_doc, depr_series, depr_schedule, asset)

	credit_entry, debit_entry = depr_module.get_credit_and_debit_entry(
		credit_account, depr_schedule, asset, depr_cost_center, debit_account, accounting_dimensions
	)
	je.append("accounts", credit_entry)
	je.append("accounts", debit_entry)

	je.flags.ignore_permissions = True
	je.save()


def prevent_duplicate_submission(doc, method=None):
	"""Journal Entry before_submit: block a second depreciation entry for an already booked schedule row."""
	if doc.voucher_type != "Depreciation Entry":
		return

	from erpnext.assets.doctype.asset_depreciation_schedule.asset_depreciation_schedule import get_depr_schedule

	for row in doc.get("accounts"):
		if row.reference_type != "Asset" or not row.reference_name or not row.debit:
			continue
		if not frappe.db.get_value("Asset", row.reference_name, "calculate_depreciation"):
			continue

		precision = row.precision("debit")
		matches = [
			d
			for d in get_depr_schedule(row.reference_name, "Active", doc.finance_book) or []
			if getdate(d.schedule_date) == getdate(doc.posting_date)
			and flt(d.depreciation_amount, precision) == flt(row.debit, precision)
		]
		if matches and all(d.journal_entry for d in matches):
			frappe.throw(
				_("Depreciation for asset {0} on {1} is already booked in {2}").format(
					row.reference_name, doc.posting_date, matches[0].journal_entry
				),
				title=_("Duplicate Depreciation Entry"),
			)


_signature_ok = list(inspect.signature(_original).parameters) == _EXPECTED_PARAMS


def apply():
	"""Called from before_request / before_job. If erpnext changed the function, keep its default (auto-submit)."""
	if _signature_ok:
		depr_module._make_journal_entry_for_depreciation = make_journal_entry_for_depreciation
