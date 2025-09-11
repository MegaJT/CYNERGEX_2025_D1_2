from config_loader import config_loader

# Load configurations
SCORE_COLORS = config_loader.get_score_colors()
SEGMENTS = config_loader.get_segments()
MONTH_DICT = config_loader.get_month_mapping()
QUARTER_DICT = config_loader.get_quarter_mapping()
BRANCH_METRIC_GROUPS = config_loader.get_metric_groups()
GROUP_WEIGHT_VARS = config_loader.get_weight_variables()

# Load Contact Centre configurations
CONTACT_CENTRE_METRIC_GROUPS = config_loader.get_contact_centre_metric_groups()
CONTACT_CENTRE_WEIGHT_VARS = config_loader.get_contact_centre_weight_variables()

# Load Website configurations
WEBSITE_METRIC_GROUPS = config_loader.get_website_metric_groups()
WEBSITE_WEIGHT_VARS = config_loader.get_website_weight_variables()

# Load Social Media configurations
SOCIAL_MEDIA_METRIC_GROUPS = config_loader.get_social_media_metric_groups()
SOCIAL_MEDIA_WEIGHT_VARS = config_loader.get_social_media_weight_variables()

# Load Combinined Contact Centre configurations
COMBINED_CONTACT_CENTRE_METRIC_GROUPS = (
    config_loader.get_combined_contact_centre_metric_groups()
)
COMBINED_CONTACT_CENTRE_WEIGHT_VARS = (
    config_loader.get_combined_contact_centre_weight_variables()
)
