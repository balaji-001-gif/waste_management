app_name = "waste_management"
app_title = "Waste Management"
app_publisher = "Your Company"
app_description = "Smart AI-Based Waste Management Application for ERPNext V15+"
app_email = "info@yourcompany.com"
app_license = "MIT"
app_version = "1.0.0"

# Apps
# ------------------
required_apps = ["frappe", "erpnext"]

# Includes in <head>
# ------------------
app_include_css = "/assets/waste_management/css/waste_management.css"
app_include_js = "/assets/waste_management/js/waste_management.js"

# Document Events
doc_events = {
    "Waste Collection Request": {
        "on_submit": [
            "waste_management.waste_management.doctype.waste_collection_request.waste_collection_request.on_submit",
        ],
        "on_cancel": [
            "waste_management.waste_management.doctype.waste_collection_request.waste_collection_request.on_cancel",
        ],
    },
    "Waste Collection Schedule": {
        "before_save": [
            "waste_management.waste_management.doctype.waste_collection_schedule.waste_collection_schedule.before_save",
        ],
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "waste_management.waste_management.doctype.ai_waste_prediction.ai_waste_prediction.run_daily_prediction",
        "waste_management.waste_management.doctype.waste_collection_schedule.waste_collection_schedule.auto_generate_schedule",
    ],
    "hourly": [
        "waste_management.waste_management.doctype.waste_vehicle.waste_vehicle.update_vehicle_status",
    ],
    "weekly": [
        "waste_management.waste_management.doctype.ai_waste_prediction.ai_waste_prediction.retrain_model",
    ],
}

# Fixtures
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "Waste Management"]],
    },
    {
        "doctype": "Property Setter",
        "filters": [["module", "=", "Waste Management"]],
    },
    {
        "doctype": "Workspace",
        "filters": [["module", "=", "Waste Management"]],
    },
]

# Permissions
has_permission = {
    "Waste Collection Request": "waste_management.waste_management.doctype.waste_collection_request.waste_collection_request.has_permission",
}

# Notification config
notification_config = "waste_management.waste_management.notification.waste_notifications.get_notification_config"

# Website
website_route_rules = [
    {
        "from_route": "/waste-portal/<name>",
        "to_route": "waste_portal",
    }
]

# Override Whitelisted Methods
override_whitelisted_methods = {}

# Jinja
jinja = {
    "methods": [
        "waste_management.waste_management.utils.jinja_methods",
    ]
}

# On app install
after_install = "waste_management.setup.install.after_install"
after_migrate = "waste_management.setup.install.after_migrate"
