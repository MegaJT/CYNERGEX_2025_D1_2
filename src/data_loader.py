import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import MONTH_DICT, BRANCH_METRIC_GROUPS, GROUP_WEIGHT_VARS
import math

def load_data(data_file, segment):
    """Load data from CSV file and preprocess it"""
    try:
        # Set pandas option to handle future behavior
        pd.set_option('future.no_silent_downcasting', True)
        
        df = pd.read_csv(data_file, index_col=False)
        # Replace empty strings with NaN and handle downcasting explicitly
        df = df.replace(r'^\s*$', np.nan, regex=True)
        df = df.infer_objects(copy=False)
        
        # Common SC_NAME mapping for all segments
        sc_name_mapping = {
            1: 'Mona Slim',
            2: 'Omar AlBaba',
            3: 'Abdulhalim Shousha',
            4: 'Mohammad Malla',
            5: 'Lyka Camba',
            6: 'Majd Tabbal',
            7: 'Osama ElNashar',
            8: 'AlNaddi Hoar',
            9: 'Abul Hassan',
            10: 'AlMeqdad Dayoub',
            11: 'Eidarous Eidarous',
            12: 'Fatima Hotait',
            13: 'Rolan Dawood',
            14: 'Adham Elhalaby',
            15: 'Jennie Villanueva',
            16: 'Hiba Taha',
            17: 'Yaman Zaitoun',
            18: 'Ahmed Elhusseini',
            19: 'NO SC ASSIGNED',
        }
        
        if segment == 'Branch':
            try:
                df['Branch'] = df['Branch'].map({1: 'Dubai', 2: 'Sharjah', 3: 'Abu Dhabi'})
                df['NATIONALITY'] = df['NATIONALITY'].map({1: 'Emarati', 2: 'Non-Emarati'})
                df['Q1_1'] = df['Q1_1'].map({1: 'Social Media Lead', 2: 'Website Visit Lead', 3: 'Call centre Lead', 4: 'Walkin Customer'})
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
                if 'SC_NAME' in df.columns:
                    df['SC_NAME'] = df['SC_NAME'].map(sc_name_mapping)
            except Exception as e:
                df = pd.DataFrame()
        
        elif segment == 'Contact Centre':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
                if 'SC_NAME' in df.columns:
                    df['SC_NAME'] = df['SC_NAME'].map(sc_name_mapping)
                
            except Exception as e:
                df = pd.DataFrame()
        
        elif segment == 'Social Media':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
                if 'SC_NAME' in df.columns:
                    df['SC_NAME'] = df['SC_NAME'].map(sc_name_mapping)
            except Exception as e:
                df = pd.DataFrame()
        
        elif segment == 'Website':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
                if 'SC_NAME' in df.columns:
                    df['SC_NAME'] = df['SC_NAME'].map(sc_name_mapping)

            except Exception as e:
                df = pd.DataFrame()

        elif segment == 'Combined Contact Centre':
            try:
                df['WAVE'] = df['WAVE'].map(MONTH_DICT)
                if 'SC_NAME' in df.columns:
                    df['SC_NAME'] = df['SC_NAME'].map(sc_name_mapping)
                   
            except Exception as e:
                df = pd.DataFrame()
            
        return df
    except Exception as e:
        return pd.DataFrame()

def filter_data_by_user(df, user_id):
    """
    Filter dataframe based on user ID
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        user_id (str): User ID to filter by (Admin sees all data)
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if df.empty:
        return df
        
    if user_id == 'Admin':
        return df
    
    # Check if 'Branch' column exists
    if 'Branch' in df.columns:
        return df[df['Branch'] == user_id]
    else:
        return df  # Return unfiltered if no Branch column

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

def load_branch_data(user_id=None):
    """
    Load branch data and prepare it for the dashboard, filtered by user_id if provided
    
    Args:
        user_id (str, optional): User ID to filter data by branch. Admin sees all data.
    
    Returns:
        tuple: (branch_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names)
    """
    # Load the branch evaluation data
    branch_df = load_data('CHERY_BRANCH_EVAL_DASH CSV.csv', 'Branch')
    
    if branch_df.empty:
        return branch_df, pd.DataFrame(), [], [], [], [], []
    
    # Filter data by user_id if provided
    if user_id and user_id != 'Admin':
        branch_df = filter_data_by_user(branch_df, user_id)
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(branch_df)
    
    # Get unique values for filters
    branches = get_unique_values(branch_df, 'Branch', ['Dubai', 'Sharjah', 'Abu Dhabi'])
    appointment_types = get_unique_values(branch_df, 'Q1_1', ['Walk-in', 'Appointment'])
    nationalities = get_unique_values(branch_df, 'NATIONALITY', ['Local', 'Expat'])
    sc_names = get_unique_values(branch_df, 'SC_NAME', [])
    
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(branch_df, AVAILABLE_MONTHS, 'branch')
    
    return branch_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names

def load_contact_centre_data(user_id=None):
    """
    Load contact centre data and prepare it for the dashboard
    
    Args:
        user_id (str, optional): User ID to filter data by branch. Admin sees all data.
    
    Returns:
        tuple: (contact_centre_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names)
    """
    # Load the contact centre evaluation data
    contact_centre_df = load_data('CHERY_CONTACT_CENTRE_EVAL_DASH CSV.csv', 'Contact Centre')
    
    if contact_centre_df.empty:
        return contact_centre_df, pd.DataFrame(), [], [], [], [], []
    
    # Filter data by user_id if provided
    if user_id and user_id != 'Admin':
        contact_centre_df = filter_data_by_user(contact_centre_df, user_id)
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(contact_centre_df)
    
    # Get unique values for filters
    branches = ['Overall']
    appointment_types = ['Overall']
    nationalities = ['Overall']
    sc_names = get_unique_values(contact_centre_df, 'SC_NAME', [])
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(contact_centre_df, AVAILABLE_MONTHS, 'contact-centre')
    
    return contact_centre_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names

def load_website_data(user_id=None):
    """
    Load website data and prepare it for the dashboard
    
    Args:
        user_id (str, optional): User ID to filter data by branch. Admin sees all data.
    
    Returns:
        tuple: (website_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names)
    """
    # Load the website evaluation data
    website_df = load_data('CHERY_WEBSITE_EVAL_DASH CSV.csv', 'Website')
    
    if website_df.empty:
        return website_df, pd.DataFrame(), [], [], [], [], []
    
    # Filter data by user_id if provided
    if user_id and user_id != 'Admin':
        website_df = filter_data_by_user(website_df, user_id)
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(website_df)
    
    # Get unique values for filters
    branches = ['Overall']
    appointment_types = ['Overall']
    nationalities = ['Overall']
    sc_names = get_unique_values(website_df, 'SC_NAME', [])
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(website_df, AVAILABLE_MONTHS, 'website')
    
    return website_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names

def load_combined_contact_centre_data(user_id=None):
    
    # Load the CC combine evaluation data
    cc_combined_df = load_data('CONTACT_CENTRE_CON CSV.csv', 'Combined Contact Centre')
    
    

    if cc_combined_df.empty:
        return cc_combined_df, pd.DataFrame(), [], [], [], [], []
    
    # Filter data by user_id if provided
    if user_id and user_id != 'Admin':
        cc_combined_df = filter_data_by_user(cc_combined_df, user_id)
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(cc_combined_df)
    
    # Get unique values for filters
    branches = ['Overall']
    appointment_types = ['Overall']
    nationalities = ['Overall']
    sc_names = get_unique_values(cc_combined_df, 'SC_NAME', [])
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(cc_combined_df, AVAILABLE_MONTHS, 'combined-contact-centre')
    
    return cc_combined_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names

def load_social_media_data(user_id=None):
    """
    Load social media data and prepare it for the dashboard
    
    Args:
        user_id (str, optional): User ID to filter data by branch. Admin sees all data.
    
    Returns:
        tuple: (social_media_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names)
    """
    # Load the social media evaluation data
    social_media_df = load_data('CHERY_SOCIAL_EVAL_DASH CSV.csv', 'Social Media')
    
    if social_media_df.empty:
        return social_media_df, pd.DataFrame(), [], [], [], [], []
    
    # Filter data by user_id if provided
    if user_id and user_id != 'Admin':
        social_media_df = filter_data_by_user(social_media_df, user_id)
    
    # Get available months
    AVAILABLE_MONTHS = get_available_months(social_media_df)
    
    # Get unique values for filters
    branches = ['Overall']
    appointment_types = ['Overall']
    nationalities = ['Overall']
    sc_names = get_unique_values(social_media_df, 'SC_NAME', [])
    
    # Prepare dashboard data
    processed_data = prepare_dashboard_data(social_media_df, AVAILABLE_MONTHS, 'social-media')
    
    return social_media_df, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities, sc_names

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
    elif segment == 'contact-centre':
        from config import CONTACT_CENTRE_METRIC_GROUPS, CONTACT_CENTRE_WEIGHT_VARS
        metric_groups = CONTACT_CENTRE_METRIC_GROUPS
        weight_vars = CONTACT_CENTRE_WEIGHT_VARS
    elif segment == 'website':
        from config import WEBSITE_METRIC_GROUPS, WEBSITE_WEIGHT_VARS
        metric_groups = WEBSITE_METRIC_GROUPS
        weight_vars = WEBSITE_WEIGHT_VARS
    elif segment == 'social-media':
        from config import SOCIAL_MEDIA_METRIC_GROUPS, SOCIAL_MEDIA_WEIGHT_VARS
        metric_groups = SOCIAL_MEDIA_METRIC_GROUPS
        weight_vars = SOCIAL_MEDIA_WEIGHT_VARS
    elif segment == 'combined-contact-centre':
        from config import COMBINED_CONTACT_CENTRE_METRIC_GROUPS, COMBINED_CONTACT_CENTRE_WEIGHT_VARS
        metric_groups = COMBINED_CONTACT_CENTRE_METRIC_GROUPS
        weight_vars = COMBINED_CONTACT_CENTRE_WEIGHT_VARS    
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
            group_score = int(round(group_score, 0)) if not math.isnan(group_score) else group_score
            
            
            # Calculate monthly scores for the group
            monthly_scores = {}
            for month in AVAILABLE_MONTHS:
                month_df = df[df['WAVE'] == month]
                if not month_df.empty and weight_var in month_df.columns:
                    month_score = calculate_metric_score(month_df, weight_var)
                    #monthly_scores[month] = int(round(month_score, 0))
                    monthly_scores[month] = int(round(month_score, 0)) if not math.isnan(month_score) else month_score

            
            # Add group score as a special entry
            processed_data.append({
                'segment': segment,
                'group': group_name,
                'metric_id': weight_var,
                'metric': f"{group_name} OVERALL",
                'score': round(group_score, 0),
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
                        #monthly_scores[month] = round(month_score, 0)
                        monthly_scores[month] = int(round(month_score, 0)) if not math.isnan(month_score) else month_score
                
                # Add to processed data
                processed_data.append({
                    'segment': segment,
                    'group': group_name,
                    'metric_id': metric_id,
                    'metric': metric_name,
                    'score': round(current_score, 0),
                    'monthly_scores': monthly_scores,
                    'is_group_score': False
                })
    
    
    if processed_data:
        return pd.DataFrame(processed_data)
    else:
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=['segment', 'group', 'metric_id', 'metric', 'score', 'monthly_scores', 'is_group_score'])

def filter_data(df, branch, appointment_type, month, nationality, sc_name):
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
        
    # Handle Sales Consultant filter using SC_NAME column
    if sc_name != "Overall" and 'SC_NAME' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['SC_NAME'] == sc_name]
            
    return filtered_df
