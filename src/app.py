import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd

# Import from our modules
from data_loader import load_branch_data, load_contact_center_data, load_website_data, load_social_media_data, prepare_dashboard_data
from layout_components import create_segment_layout
from callbacks import register_callbacks
from config import SEGMENTS

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
server = app.server

# Load the data for each segment
branch_df, branch_processed_data, branch_available_months, branch_branches, branch_appointment_types, branch_nationalities = load_branch_data()
contact_center_df, contact_center_processed_data, contact_center_available_months, _, _, _ = load_contact_center_data()
website_df, website_processed_data, website_available_months, _, _, _ = load_website_data()
social_media_df, social_media_processed_data, social_media_available_months, _, _, _ = load_social_media_data()

# Combine processed data
processed_data = pd.concat([branch_processed_data, contact_center_processed_data, website_processed_data, social_media_processed_data], ignore_index=True)

# Define the app layout
app.layout = html.Div([
    # Store the current segment
    dcc.Store(id='current-segment', data='branch'),
    
    # Header row
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url('logo5.png'), className="logo")
        ], width=2),
        dbc.Col([
            html.H1("CHERY UAE Mystery Shopping Dashboard")
        ], width=8, className="text-center"),
        dbc.Col([
            html.Img(src=app.get_asset_url('CYN_Logo1.png'), className="logo float-right")
        ], width=2)
    ], className="header-row mb-4"),
    
    # Tabs for different segments
    dbc.Tabs([
        dbc.Tab(label=SEGMENTS['branch'], tab_id='branch'),
        dbc.Tab(label=SEGMENTS['contact-center'], tab_id='contact-center'),
        dbc.Tab(label=SEGMENTS['website'], tab_id='website'),
        dbc.Tab(label=SEGMENTS['social-media'], tab_id='social-media'),
    ], id='segment-tabs', active_tab='branch', className="mb-4"),
    
    # Content div - will be populated based on selected tab
    html.Div(id='segment-content')
], className="dashboard-container")

# Register all callbacks
register_callbacks(app, branch_df, contact_center_df, website_df, social_media_df, processed_data, 
                  branch_available_months, contact_center_available_months, website_available_months, social_media_available_months)

if __name__ == "__main__":
    app.run(debug=True)
