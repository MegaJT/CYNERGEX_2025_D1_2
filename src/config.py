from config_loader import config_loader

# Load configurations
SCORE_COLORS = config_loader.get_score_colors()
SEGMENTS = config_loader.get_segments()
MONTH_DICT = config_loader.get_month_mapping()
BRANCH_METRIC_GROUPS = config_loader.get_metric_groups()
GROUP_WEIGHT_VARS = config_loader.get_weight_variables()

# Load Contact Center configurations
CONTACT_CENTER_METRIC_GROUPS = config_loader.get_contact_center_metric_groups()
CONTACT_CENTER_WEIGHT_VARS = config_loader.get_contact_center_weight_variables()

# Load Website configurations
WEBSITE_METRIC_GROUPS = config_loader.get_website_metric_groups()
WEBSITE_WEIGHT_VARS = config_loader.get_website_weight_variables() 