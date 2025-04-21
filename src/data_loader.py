import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import MONTH_DICT, BRANCH_METRIC_GROUPS, GROUP_WEIGHT_VARS

def load_data(data_file, segment):
    """Load data from CSV file and preprocess it"""
    try:
        # Set pandas option to handle future behavior
        pd.set_option('future.no_silent_downcasting', True)
        
        df = pd.read_csv(data_file, index_col=False)
        # Replace empty strings with NaN and handle downcasting explicitly
        df = df.replace(r'^\s*$', np.nan, regex=True)
        df = df.infer_objects(copy=False)
        
        if segment == 'Branch':
            try:
                df['Branch'] = df['Branch'].map({1: 'Dubai', 2: 'Sharjah', 3: 'Abu Dhabi'})
                df['NATIONALITY'] = df['NATIONALITY'].map({1: 'Emarati', 2: 'Non-Emarati'})
                df['Q1_1'] = df['Q1_1'].map({1: 'Social Media Lead', 2: 'Website Visit Lead', 3: 'Call Centre Lead', 4: 'Walkin Customer'})
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
            except:
                df = pd.DataFrame()  # Create empty dataframe if mapping fails
        
        elif segment == 'Contact Centre':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
            except:
                df = pd.DataFrame()
        
        elif segment == 'social media':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
            except:
                df = pd.DataFrame()
        
        elif segment == 'Website':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
            except:
                df = pd.DataFrame()
                
        return df
    except:
        return pd.DataFrame()  # Return empty dataframe if file not found

def get_available_months(df):
    """Get available months from the data"""
    if df.empty or 'WAVE' not in df.columns:
        return []
    
    # Get unique months and sort them
    months = df['WAVE'].dropna().unique().tolist()
    return months if months else []

def get_unique_values(df, column_name, default=None):
    """Get unique values from a column in the dataframe"""
    if column_name in df.columns:
        values = df[column_name].dropna().unique().tolist()
        return values if values else default
    return default

def calculate_metric_score(df, metric_column):
    """Calculate mean score for a metric, ignoring NA values"""
    if df.empty or metric_column not in df.columns:
        return 0
    
    # Convert column to numeric, coercing errors to NaN
    numeric_values = pd.to_numeric(df[metric_column], errors='coerce')
    
    # Calculate mean, dropping NaN values
    return numeric_values.dropna().mean() if not numeric_values.empty else 0

def load_branch_data():
    """Load branch data and prepare it for the dashboard"""
    # Load the branch evaluation data
    branch_df = load_data('S_BRANCH_EVAL CSV.csv', 'Branch')
    
    if branch_df.empty:
        return branch_df, pd.DataFrame(), [], [], [], []
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(branch_df)
    
    # Get unique values for filters
    branches = get_unique_values(branch_df, 'Branch', ['Dubai', 'Sharjah', 'Abu Dhabi'])
    appointment_types = get_unique_values(branch_df, 'Q1_1', ['Walk-in', 'Appointment'])
    nationalities = get_unique_values(branch_df, 'NATIONALITY', ['Local', 'Expat'])
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(branch_df, AVAILABLE_MONTHS, 'branch')
    
    return branch_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities

def load_contact_center_data():
    """Load contact center data and prepare it for the dashboard"""
    # Load the contact center evaluation data
    contact_center_df = load_data('S_CONTACT_CENTRE CSV.csv', 'Contact Centre')
    
    if contact_center_df.empty:
        return contact_center_df, pd.DataFrame(), [], [], [], []
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(contact_center_df)
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(contact_center_df, AVAILABLE_MONTHS, 'contact-center')
    
    return contact_center_df, processed_data, AVAILABLE_MONTHS, [], [], []

def load_website_data():
    """Load website data and prepare it for the dashboard"""
    # Load the website evaluation data
    website_df = load_data('S_WEBSITE_EVAL CSV.csv', 'Website')
    
    if website_df.empty:
        return website_df, pd.DataFrame(), [], [], [], []
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(website_df)
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(website_df, AVAILABLE_MONTHS, 'website')
    
    return website_df, processed_data, AVAILABLE_MONTHS, [], [], []

def load_social_media_data():
    """Load social media data and prepare it for the dashboard"""
    # Load the social media evaluation data
    social_media_df = load_data('S_SM_EVAL CSV.csv', 'social media')
    
    if social_media_df.empty:
        return social_media_df, pd.DataFrame(), [], [], [], []
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(social_media_df)
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(social_media_df, AVAILABLE_MONTHS, 'social-media')
    
    return social_media_df, processed_data, AVAILABLE_MONTHS, [], [], []

def prepare_dashboard_data(df, AVAILABLE_MONTHS=None, segment=None):
    """Prepare data for the dashboard"""
    if df.empty:
        return pd.DataFrame(columns=['segment', 'group', 'metric_id', 'metric', 'score', 'monthly_scores', 'is_group_score'])
    
    # If no months are provided, get them from the dataframe
    if AVAILABLE_MONTHS is None:
        AVAILABLE_MONTHS = get_available_months(df)
    
    # Create a list to store processed data
    processed_data = []
    
    # Get the appropriate metric groups and weight variables based on segment
    if segment == 'branch':
        metric_groups = BRANCH_METRIC_GROUPS
        weight_vars = GROUP_WEIGHT_VARS
    elif segment == 'contact-center':
        from config import CONTACT_CENTER_METRIC_GROUPS, CONTACT_CENTER_WEIGHT_VARS
        metric_groups = CONTACT_CENTER_METRIC_GROUPS
        weight_vars = CONTACT_CENTER_WEIGHT_VARS
    elif segment == 'website':
        from config import WEBSITE_METRIC_GROUPS, WEBSITE_WEIGHT_VARS
        metric_groups = WEBSITE_METRIC_GROUPS
        weight_vars = WEBSITE_WEIGHT_VARS
    elif segment == 'social-media':
        from config import SOCIAL_MEDIA_METRIC_GROUPS, SOCIAL_MEDIA_WEIGHT_VARS
        metric_groups = SOCIAL_MEDIA_METRIC_GROUPS
        weight_vars = SOCIAL_MEDIA_WEIGHT_VARS
    else:
        return pd.DataFrame(columns=['segment', 'group', 'metric_id', 'metric', 'score', 'monthly_scores', 'is_group_score'])
    
    # Process each group and its metrics
    for group_name, metrics in metric_groups.items():
        # Get the weight variable for this group
        weight_var = weight_vars.get(group_name)
        
        # If we have a weight variable and it exists in the dataframe
        if weight_var and weight_var in df.columns:
            # Calculate group score directly from the weight variable
            group_score = calculate_metric_score(df, weight_var)
            
            # Calculate monthly scores for the group
            monthly_scores = {}
            for month in AVAILABLE_MONTHS:
                month_df = df[df['WAVE'] == month]
                if not month_df.empty and weight_var in month_df.columns:
                    month_score = calculate_metric_score(month_df, weight_var)
                    monthly_scores[month] = round(month_score, 1)
            
            # Add group score as a special entry
            processed_data.append({
                'segment': segment,
                'group': group_name,
                'metric_id': weight_var,
                'metric': f"{group_name} OVERALL",
                'score': round(group_score, 1),
                'monthly_scores': monthly_scores,
                'is_group_score': True
            })
        
        # Still process individual metrics for detailed view
        for metric_id, metric_name in metrics.items():
            if metric_id in df.columns:
                # Calculate current score (mean of the metric, ignoring NA)
                current_score = calculate_metric_score(df, metric_id)
                
                # Calculate monthly scores
                monthly_scores = {}
                for month in AVAILABLE_MONTHS:
                    month_df = df[df['WAVE'] == month]
                    if not month_df.empty:
                        month_score = calculate_metric_score(month_df, metric_id)
                        monthly_scores[month] = round(month_score, 1)
                
                # Add to processed data
                processed_data.append({
                    'segment': segment,
                    'group': group_name,
                    'metric_id': metric_id,
                    'metric': metric_name,
                    'score': round(current_score, 1),
                    'monthly_scores': monthly_scores,
                    'is_group_score': False
                })
    
    # Create DataFrame from processed data
    if processed_data:
        return pd.DataFrame(processed_data)
    else:
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['segment', 'group', 'metric_id', 'metric', 'score', 'monthly_scores', 'is_group_score'])

def filter_data(df, branch, appointment_type, month, nationality):
    """Filter data based on user selections"""
    filtered_df = df.copy()
    
    if branch != "Overall" and 'Branch' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Branch'] == branch]
    
    if appointment_type != "Overall" and 'Q1_1' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Q1_1'] == appointment_type]
    
    if 'WAVE' in filtered_df.columns:
        # Handle month filtering
        if isinstance(month, list):
            if "Overall" in month:
                # If Overall is selected, show all months
                pass
            else:
                # Filter by selected months
                filtered_df = filtered_df[filtered_df['WAVE'].isin(month)]
    
    if nationality != "Overall" and 'NATIONALITY' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['NATIONALITY'] == nationality]
    
    return filtered_df
