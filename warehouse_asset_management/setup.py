import os

import frappe
from frappe.modules.import_file import import_file_by_path

# Bank versions of erpnext's Assets workspace and sidebar, re-applied after every migrate
# so that erpnext updates do not bring back the stock layout.
CORE_OVERRIDES = ("assets_workspace.json", "assets_workspace_sidebar.json")


def after_migrate():
	folder = frappe.get_app_path("warehouse_asset_management", "core_overrides")
	for filename in CORE_OVERRIDES:
		import_file_by_path(os.path.join(folder, filename), force=True)
