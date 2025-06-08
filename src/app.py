# https://cynergex-2025-d1-2.onrender.com/
# https://api.render.com/deploy/srv-d03lh0idbo4c738goj90?key=I9fsmFEvfHw


import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from datetime import timedelta
import os

# Import from our modules
from data_loader import load_branch_data, load_contact_centre_data, load_website_data, load_social_media_data,load_combined_contact_centre_data, prepare_dashboard_data
from layout_components import create_segment_layout
from callbacks import register_callbacks
from config import SEGMENTS

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
server = app.server

# Set the secret key for Flask session
server.secret_key = os.environ.get('SECRET_KEY', 'Welcome101')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# User class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Valid access codes (in a real app, store these securely in a database)
VALID_CODES = {
    '5823': 'Admin',
    '1947': 'Dubai',
    '7365': 'Sharjah',
    '4091': 'Abu Dhabi',
}

server.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(days=1),  # Increase session lifetime
    REMEMBER_COOKIE_DURATION=timedelta(days=1)
)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Login layout
login_layout = html.Div([
    html.Div([
        html.Img(src='assets/logo5.png', style={'height': '100px'}),
        html.H1('Mystery Shopping Dashboard Login'),
        
    ], className='login-banner'),
    
    html.Div([
        html.Div([
            html.H2('Enter Access Code'),
            dcc.Input(
                id='access-code',
                type='password',
                placeholder='Enter 4-digit code',
                maxLength=4,
                minLength=4,
                className='login-input'
            ),
            html.Button('Login', id='login-button', className='login-button'),
            html.Div(id='login-error', className='login-error',children='')
        ], className='login-form')
    ], className='login-container')
], className='login-page')

# Global data store for pre-filtered data
app.user_data = {}

# Load and pre-filter data for all users
def load_all_data():
    # Load the raw data for each segment
    branch_df, branch_processed_data, branch_available_months, branch_branches, branch_appointment_types, branch_nationalities, branch_sc_names = load_branch_data()
    contact_centre_df, contact_centre_processed_data, contact_centre_available_months, _, _, _, contact_centre_sc_names = load_contact_centre_data()
    website_df, website_processed_data, website_available_months, _, _, _, website_sc_names = load_website_data()
    social_media_df, social_media_processed_data, social_media_available_months, _, _, _, social_media_sc_names = load_social_media_data()
    combined_contact_centre_df, combined_contact_centre_processed_data, combined_contact_centre_available_months, _, _, _, combined_contact_centre_sc_names = load_combined_contact_centre_data()
    
    
    # Pre-filter branch data for each user
    for user_id in VALID_CODES.values():
        if user_id == 'Admin':
            # Admin sees all data
            filtered_branch_df = branch_df.copy()
            filtered_branch_processed = branch_processed_data.copy()
            filtered_branches = branch_branches.copy()
            # Combine SC names from all segments
            all_sc_names = list(set(branch_sc_names + contact_centre_sc_names + website_sc_names + social_media_sc_names))
            filtered_sc_names = sorted(all_sc_names) if all_sc_names else branch_sc_names.copy()
            
        else:
            # Filter data for specific branch/location
            filtered_branch_df = branch_df[branch_df['Branch'].str.contains(user_id, case=False)]
            filtered_branches = [b for b in branch_branches if user_id.lower() in b.lower()]
            # Combine SC names from all segments for this branch
            all_sc_names = list(set(branch_sc_names + contact_centre_sc_names + website_sc_names + social_media_sc_names))
            filtered_sc_names = sorted(all_sc_names) if all_sc_names else branch_sc_names.copy()
            
        
        # Store pre-filtered data for this user
        app.user_data[user_id] = {
            'branch': {
                'df': filtered_branch_df,
                'processed': filtered_branch_processed,
                'months': branch_available_months,
                'branches': filtered_branches,
                'appointment_types': branch_appointment_types,
                'nationalities': branch_nationalities,
                'sc_names': filtered_sc_names
            },
            'contact-centre': {
                'df': contact_centre_df,
                'processed': contact_centre_processed_data,
                'months': contact_centre_available_months,
                'sc_names': contact_centre_sc_names
            },
            'website': {
                'df': website_df,
                'processed': website_processed_data,
                'months': website_available_months,
                'sc_names': website_sc_names
            },
            'social-media': {
                'df': social_media_df,
                'processed': social_media_processed_data,
                'months': social_media_available_months,
                'sc_names': social_media_sc_names
            },
            'combined-contact-centre': {
                'df': combined_contact_centre_df,
                'processed': combined_contact_centre_processed_data,
                'months': combined_contact_centre_available_months,
                'sc_names': combined_contact_centre_sc_names
            }
        }
        
        # Create combined processed data for this user
        app.user_data[user_id]['combined_processed'] = pd.concat([
            filtered_branch_processed,
            contact_centre_processed_data,
            website_processed_data,
            social_media_processed_data,
            contact_centre_processed_data
        ], ignore_index=True)

# Load data at startup
load_all_data()

# Create the dashboard layout function
def create_dashboard_layout(user_id):
    return html.Div([
        # Store the current segment and user ID
        dcc.Store(id='current-segment', data='branch'),
        dcc.Store(id='user-id', data=user_id),  # Store user ID for filtering
        
        # Header row
        dbc.Row([
            dbc.Col([
                html.Img(src=app.get_asset_url('logo5.png'), className="logo")
            ], width=2),
            dbc.Col([
                html.H1("CHERY UAE Mystery Shopping Dashboard")
            ], width=8, className="text-center"),
            dbc.Col([
                html.Div(
                html.Img(src=app.get_asset_url('CYN_Logo2.png'), className="logo float-right")
            )], width=2)
        ], className="header-row mb-4"),
        
        # Tabs for different segments
        dbc.Tabs([
            dbc.Tab(label=SEGMENTS['branch'], tab_id='branch'),
            dbc.Tab(label=SEGMENTS['contact-centre'], tab_id='contact-centre'),
            dbc.Tab(label=SEGMENTS['website'], tab_id='website'),
            dbc.Tab(label=SEGMENTS['social-media'], tab_id='social-media'),
            dbc.Tab(label=SEGMENTS['combined-contact-centre'], tab_id='combined-contact-centre'),
        ], id='segment-tabs', active_tab='branch', className="mb-4"),
        
        # Content div - will be populated based on selected tab
        html.Div(id='segment-content')
    ], className="dashboard-container")

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

# Callbacks for login functionality
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    # Check if user is authenticated
    if not current_user.is_authenticated:
        return login_layout
    
    # User is authenticated, show the dashboard with user_id
    return create_dashboard_layout(current_user.id)

@app.callback(
    [Output('url', 'pathname'),
     Output('login-error', 'children')],
    Input('login-button', 'n_clicks'),
    State('access-code', 'value'),
    prevent_initial_call=True
)
def login_user_callback(n_clicks, access_code):
    if n_clicks is None:
        raise PreventUpdate
    
    if access_code in VALID_CODES:
        user_id = VALID_CODES[access_code]
        login_user(User(user_id), remember=True)  # Set remember=True
        return '/', ''
    else:
        return '/login', 'Invalid access code. Please try again.'

@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout_user_callback(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    
    logout_user()
    return '/login'


# Register other callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
