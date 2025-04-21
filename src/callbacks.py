from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
from data_loader import filter_data,  prepare_dashboard_data
from layout_components import create_segment_layout, create_group_section

def register_callbacks(app, branch_df, contact_center_df, website_df, social_media_df, processed_data, 
                      branch_available_months, contact_center_available_months, website_available_months, social_media_available_months):
    """Register all callbacks for the application"""
    
    # Callback to update content based on selected tab
    @app.callback(
        Output('segment-content', 'children'),
        Output('current-segment', 'data'),
        Input('segment-tabs', 'active_tab')
    )
    def render_segment_content(active_tab):
        if active_tab:
            # Get unique values for filters based on segment
            if active_tab == 'branch':
                branches = branch_df['Branch'].dropna().unique().tolist() if 'Branch' in branch_df.columns else ['Dubai', 'Sharjah', 'Abu Dhabi']
                appointment_types = branch_df['Q1_1'].dropna().unique().tolist() if 'Q1_1' in branch_df.columns else ['Walk-in', 'Appointment']
                nationalities = branch_df['NATIONALITY'].dropna().unique().tolist() if 'NATIONALITY' in branch_df.columns else ['Local', 'Expat']
                available_months = branch_available_months
            elif active_tab == 'contact-center':
                branches = ['Overall']
                appointment_types = ['Overall']
                nationalities = ['Overall']
                available_months = contact_center_available_months
            elif active_tab == 'website':
                branches = ['Overall']
                appointment_types = ['Overall']
                nationalities = ['Overall']
                available_months = website_available_months
            elif active_tab == 'social-media':
                branches = ['Overall']
                appointment_types = ['Overall']
                nationalities = ['Overall']
                available_months = social_media_available_months
            else:
                branches = ['Overall']
                appointment_types = ['Overall']
                nationalities = ['Overall']
                available_months = []
            
            return create_segment_layout(active_tab, processed_data, available_months, branches, appointment_types, nationalities), active_tab
        return "Select a segment to view data.", 'branch'

    # Add callback for month filter validation
    for segment in ['branch', 'contact-center', 'website', 'social-media']:
        @app.callback(
            Output(f"{segment}-month-filter", "value"),
            Input(f"{segment}-month-filter", "value")
        )
        def validate_month_selection(selected_months, segment=segment):
            if not selected_months:  # If no months are selected
                return ["Overall"]  # Default to Overall
            return selected_months

    @app.callback(
    Output(f"branch-groups-container", "children"),
    Output(f"branch-visit-count", "children"),
    [Input(f"branch-branch-filter", "value"),
     Input(f"branch-appointment-filter", "value"),
     Input(f"branch-month-filter", "value"),
     Input(f"branch-nationality-filter", "value")]
    )
    def update_branch_content(branch, appointment_type, month, nationality):
        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(branch_df, branch, appointment_type, month, nationality)
        
        # Update visit count
        visit_count = len(filtered_raw_df)
        
        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(filtered_raw_df, branch_available_months, 'branch')
        
        # Get the branch segment data
        df_segment = filtered_processed_data[filtered_processed_data['segment'] == 'branch']
        
        # Get unique groups
        groups = df_segment['group'].unique()
        
        # Create updated group sections
        updated_group_sections = [
            create_group_section('branch', group, df_segment) for group in groups
        ]
        
        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for contact-center segment
    @app.callback(
        Output(f"contact-center-groups-container", "children"),
        Output(f"contact-center-visit-count", "children"),
        Input(f"contact-center-month-filter", "value")
    )
    def update_contact_center_content(month):
        # Filter the raw dataframe based on month selection
        filtered_raw_df = filter_data(contact_center_df, "Overall", "Overall", month, "Overall")
        
        # Update visit count
        visit_count = len(filtered_raw_df)
        
        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(filtered_raw_df, contact_center_available_months, 'contact-center')
        
        # Get the contact-center segment data
        df_segment = filtered_processed_data[filtered_processed_data['segment'] == 'contact-center']
        
        # Get unique groups
        groups = df_segment['group'].unique()
        
        # Create updated group sections
        updated_group_sections = [
            create_group_section('contact-center', group, df_segment) for group in groups
        ]
        
        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for website segment
    @app.callback(
        Output(f"website-groups-container", "children"),
        Output(f"website-visit-count", "children"),
        Input(f"website-month-filter", "value")
    )
    def update_website_content(month):
        # Filter the raw dataframe based on month selection
        filtered_raw_df = filter_data(website_df, "Overall", "Overall", month, "Overall")
        
        # Update visit count
        visit_count = len(filtered_raw_df)
        
        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(filtered_raw_df, website_available_months, 'website')
        
        # Get the website segment data
        df_segment = filtered_processed_data[filtered_processed_data['segment'] == 'website']
        
        # Get unique groups
        groups = df_segment['group'].unique()
        
        # Create updated group sections
        updated_group_sections = [
            create_group_section('website', group, df_segment) for group in groups
        ]
        
        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for social-media segment
    @app.callback(
        Output(f"social-media-groups-container", "children"),
        Output(f"social-media-visit-count", "children"),
        Input(f"social-media-month-filter", "value")
    )
    def update_social_media_content(month):
        # Filter the raw dataframe based on month selection
        filtered_raw_df = filter_data(social_media_df, "Overall", "Overall", month, "Overall")
        
        # Update visit count
        visit_count = len(filtered_raw_df)
        
        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(filtered_raw_df, social_media_available_months, 'social-media')
        
        # Get the social-media segment data
        df_segment = filtered_processed_data[filtered_processed_data['segment'] == 'social-media']
        
        # Get unique groups
        groups = df_segment['group'].unique()
        
        # Create updated group sections
        updated_group_sections = [
            create_group_section('social-media', group, df_segment) for group in groups
        ]
        
        return updated_group_sections, f"Base: {visit_count} Visits"
