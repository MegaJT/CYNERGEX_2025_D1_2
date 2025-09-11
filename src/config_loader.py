import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """Class to load and manage configurations from YAML files."""

    def __init__(self, config_dir: str = "config"):
        """Initialize the ConfigLoader with the configuration directory."""
        self.config_dir = config_dir
        self._configs = {}

    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load a configuration from a YAML file."""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)
                self._configs[filename] = config
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {filepath} not found")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {filepath}: {str(e)}")

    def get_config(self, filename: str) -> Dict[str, Any]:
        """Get a configuration, loading it if not already loaded."""
        if filename not in self._configs:
            return self.load_config(filename)
        return self._configs[filename]

    def get_score_colors(self) -> Dict[str, int]:
        """Get score color thresholds."""
        config = self.get_config("score_colors.yaml")
        return config["score_colors"]

    def get_segments(self) -> Dict[str, str]:
        """Get segment definitions."""
        config = self.get_config("segments.yaml")
        return config["segments"]

    def get_month_mapping(self) -> Dict[int, str]:
        """Get month mapping."""
        config = self.get_config("months.yaml")
        return config["month_mapping"]

    def get_quarter_mapping(self) -> Dict[int, str]:
        """Get quarter mapping."""
        config = self.get_config("quarters.yaml")
        return config["quarter_mapping"]

    def get_metric_groups(self) -> Dict[str, Dict[str, str]]:
        """Get metric group definitions."""
        config = self.get_config("metrics.yaml")
        return config["metric_groups"]

    def get_weight_variables(self) -> Dict[str, str]:
        """Get weight variable mappings."""
        config = self.get_config("metrics.yaml")
        return config["weight_variables"]

    def get_contact_centre_metric_groups(self) -> Dict[str, Dict[str, str]]:
        """Get Contact Centre metric group definitions."""
        config = self.get_config("contact_centre_metrics.yaml")
        return config["metric_groups"]

    def get_contact_centre_weight_variables(self) -> Dict[str, str]:
        """Get Contact Centre weight variables."""
        config = self.get_config("contact_centre_metrics.yaml")
        return config["weight_variables"]

    def get_website_metric_groups(self) -> Dict[str, Dict[str, str]]:
        """Get Website metric group definitions."""
        config = self.get_config("website_metrics.yaml")
        return config["metric_groups"]

    def get_website_weight_variables(self) -> Dict[str, str]:
        """Get Website weight variables."""
        config = self.get_config("website_metrics.yaml")
        return config["weight_variables"]

    def get_social_media_metric_groups(self) -> Dict[str, Dict[str, str]]:
        """Get Social Media metric group definitions."""
        config = self.get_config("social_media_metrics.yaml")
        return config["metric_groups"]

    def get_social_media_weight_variables(self) -> Dict[str, str]:
        """Get Social Media weight variables."""
        config = self.get_config("social_media_metrics.yaml")
        return config["weight_variables"]

    def get_combined_contact_centre_metric_groups(self) -> Dict[str, Dict[str, str]]:
        """Get Combined Contact Centre metric group definitions."""
        config = self.get_config("combined_contact_centre_metrics.yaml")
        return config["metric_groups"]

    def get_combined_contact_centre_weight_variables(self) -> Dict[str, str]:
        """Get Combined Contact Centre weight variables."""
        config = self.get_config("combined_contact_centre_metrics.yaml")
        return config["weight_variables"]


# Create a global instance
config_loader = ConfigLoader()
