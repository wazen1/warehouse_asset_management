app_name = "warehouse_asset_management"
app_title = "Warehouse Asset Management"
app_publisher = "Solvronix"
app_description = "Warehouse Asset Management App"
app_email = "admin@solvronix.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "warehouse_asset_management",
# 		"logo": "/assets/warehouse_asset_management/logo.png",
# 		"title": "Warehouse Asset Management",
# 		"route": "/warehouse_asset_management",
# 		"has_permission": "warehouse_asset_management.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/warehouse_asset_management/css/warehouse_asset_management.css"
# app_include_js = "/assets/warehouse_asset_management/js/warehouse_asset_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/warehouse_asset_management/css/warehouse_asset_management.css"
# web_include_js = "/assets/warehouse_asset_management/js/warehouse_asset_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "warehouse_asset_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "warehouse_asset_management/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "warehouse_asset_management.utils.jinja_methods",
# 	"filters": "warehouse_asset_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "warehouse_asset_management.install.before_install"
# after_install = "warehouse_asset_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "warehouse_asset_management.uninstall.before_uninstall"
# after_uninstall = "warehouse_asset_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "warehouse_asset_management.utils.before_app_install"
# after_app_install = "warehouse_asset_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "warehouse_asset_management.utils.before_app_uninstall"
# after_app_uninstall = "warehouse_asset_management.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "warehouse_asset_management.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "warehouse_asset_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

override_doctype_class = {"Asset": "warehouse_asset_management.overrides.asset.CustomAsset"}

override_whitelisted_methods = {
	"erpnext.assets.doctype.asset.asset.get_item_details": "warehouse_asset_management.overrides.asset.get_item_details",
}

doctype_js = {"Asset": "public/js/asset.js"}

jinja = {
	"methods": [
		"warehouse_asset_management.warehouse_asset_management.utils.asset_sticker.get_asset_sticker_qr_png_data_uri",
		"warehouse_asset_management.warehouse_asset_management.utils.asset_sticker.get_asset_sticker_barcode_png_data_uri",
	],
}

doc_events = {
	"Journal Entry": {
		"before_submit": "warehouse_asset_management.overrides.depreciation.prevent_duplicate_submission"
	},
	"Purchase Receipt": {
		"on_submit": "warehouse_asset_management.events.on_purchase_receipt_submit"
	},
	"Asset": {
		"on_submit": "warehouse_asset_management.events.on_asset_submit_or_update",
		"on_update": "warehouse_asset_management.events.on_asset_submit_or_update"
	}
}

custom_fields = {
	"Asset": [
		{
			"fieldname": "custom_asset_inventory",
			"label": "سجل تخزين الأصل",
			"fieldtype": "Link",
			"options": "Asset Inventory",
			"insert_after": "item_code",
			"read_only": 0
		}
	]
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"warehouse_asset_management.tasks.all"
# 	],
# 	"daily": [
# 		"warehouse_asset_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"warehouse_asset_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"warehouse_asset_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"warehouse_asset_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "warehouse_asset_management.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "warehouse_asset_management.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "warehouse_asset_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "warehouse_asset_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["warehouse_asset_management.overrides.depreciation.apply"]
# after_request = ["warehouse_asset_management.utils.after_request"]

# Job Events
# ----------
before_job = ["warehouse_asset_management.overrides.depreciation.apply"]
# after_job = ["warehouse_asset_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"warehouse_asset_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


fixtures = [
	{"dt": "Property Setter", "filters": [["doc_type", "=", "Asset"]]},
	{"dt": "Custom Field", "filters": [["name", "=", "Accounts Settings-require_depreciation_entry_approval"]]},
	{
		"dt": "Custom Role",
		"filters": [["report", "in", ["Asset Activity", "Asset Maintenance", "Fixed Asset Register"]]],
	},
]
