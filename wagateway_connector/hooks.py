app_name = "wagateway_connector"
app_title = "Whatsapp Gateway Connector"
app_publisher = "HomeAutomator.id"
app_description = "Connetor for Unofficial WhatsApp Gateway. Sending documents via WhatsApp"
app_email = "connect@homeautomator.id"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "wagateway_connector",
# 		"logo": "/assets/wagateway_connector/logo.png",
# 		"title": "Whatsapp Gateway Connector",
# 		"route": "/wagateway_connector",
# 		"has_permission": "wagateway_connector.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/wagateway_connector/css/wagateway_connector.css"
# app_include_js = "/assets/wagateway_connector/js/wagateway_connector.js"

# include js, css files in header of web template
# web_include_css = "/assets/wagateway_connector/css/wagateway_connector.css"
# web_include_js = "/assets/wagateway_connector/js/wagateway_connector.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "wagateway_connector/public/scss/website"

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
# app_include_icons = "wagateway_connector/public/icons.svg"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "wagateway_connector.utils.jinja_methods",
# 	"filters": "wagateway_connector.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "wagateway_connector.install.before_install"
# after_install = "wagateway_connector.install.after_install"
after_install = "wagateway_connector.contact_customizations.add_contact_custom_fields"


# Uninstallation
# ------------

# before_uninstall = "wagateway_connector.uninstall.before_uninstall"
# after_uninstall = "wagateway_connector.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "wagateway_connector.utils.before_app_install"
# after_app_install = "wagateway_connector.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "wagateway_connector.utils.before_app_uninstall"
# after_app_uninstall = "wagateway_connector.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "wagateway_connector.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = {
    "Contact": {
        "before_insert": "wagateway_connector.contact_customizations.ensure_uid",
        "validate": "wagateway_connector.contact_customizations.update_wa_address"
    },
    "Scheduled Whatsapp Message Contact": {
        "before_save": "wagateway_connector.contact_customizations.update_number"
    },
    "WAHA Session": {
        "on_update": "wagateway_connector.api.update_sched_msg_enable_flag"
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"wagateway_connector.tasks.all"
# 	],
# 	"daily": [
# 		"wagateway_connector.tasks.daily"
# 	],
# 	"hourly": [
# 		"wagateway_connector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"wagateway_connector.tasks.weekly"
# 	],
# 	"monthly": [
# 		"wagateway_connector.tasks.monthly"
# 	],
# }
scheduler_events = {
    "cron": {
        "*/5 * * * *": [  # run every 1 minute
            "wagateway_connector.tasks.send_scheduled_whatsapp_messages"
        ],
        "0 0 * * *": [  # reset at midnight
            "wagateway_connector.tasks.reset_scheduled_messages"
        ]
    }
}


# Testing
# -------

# before_tests = "wagateway_connector.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "wagateway_connector.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "wagateway_connector.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["wagateway_connector.utils.before_request"]
# after_request = ["wagateway_connector.utils.after_request"]

# Job Events
# ----------
# before_job = ["wagateway_connector.utils.before_job"]
# after_job = ["wagateway_connector.utils.after_job"]

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
# 	"wagateway_connector.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

patches = [
    "wagateway_connector.patches.add_whatsapp_medium"
]