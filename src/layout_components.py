from dash import html, dcc
import dash_bootstrap_components as dbc
from config import SCORE_COLORS
import pandas as pd

def get_score_color(score):
    """Return Bootstrap color class based on score value"""
    if score < SCORE_COLORS['danger']:
        return 'danger'
    elif score < SCORE_COLORS['warning']:
        return 'warning'
    else:
        return 'success'

def create_score_card(score, title, monthly_scores=None, color_class=""):
    """Create a score card with monthly trend data"""
    # Determine color based on score
    color = get_score_color(score)
    
    # Create trend visualization if monthly data is available
    trend_component = create_monthly_trend_chart(monthly_scores) if monthly_scores else html.Div()
    
    # Format the score display
    score_display = "N/A" if pd.isna(score) else f"{score}"
    
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.Div([
                html.H2(score_display, className=f"score-value text-{color} {color_class}"),
                html.P("/100", className="score-denominator")
            ], className="score-display"),
            trend_component
        ]),
        className="score-card"
    )

def create_monthly_trend_chart(monthly_scores):
    """Create a trend visualization for monthly scores"""
    if not monthly_scores or len(monthly_scores) <= 0:
        return html.Div()
    
    # Sort months chronologically
    months = monthly_scores.keys()
    scores = [monthly_scores[month] for month in months]
    
    # Create colored dots for each month
    trend_dots = []
    for month, score in zip(months, scores):
        color = get_score_color(score)
        # Use abbreviated month name to save space
        short_month = month
        # Format the score display
        score_display = "N/A" if pd.isna(score) else f"{score}"
        trend_dots.append(
            html.Div([
                html.Span(short_month, className="trend-month"),
                html.Span(score_display, className=f"trend-dot bg-{color}")
            ], className="trend-item")
        )
    
    return html.Div([
        html.P("Monthly Trend:", className="trend-title"),
        html.Div(trend_dots, className="trend-container")
    ], className="score-trend")

def create_group_section(segment, group_name, df_filtered):
    """Create a section for a group with its metrics"""
    # Get metrics for this group
    group_metrics = df_filtered[df_filtered['group'] == group_name]
    
    # Find the group score entry (if it exists)
    group_score_entry = group_metrics[group_metrics['is_group_score'] == True]
    
    if not group_score_entry.empty:
        # Use the pre-calculated group score from the weight variable
        group_score = group_score_entry.iloc[0]['score']
        group_monthly_scores = group_score_entry.iloc[0]['monthly_scores']
    else:
        # Fall back to calculating from individual metrics if no weight variable was found
        individual_metrics = group_metrics[group_metrics['is_group_score'] == False]
        group_score = individual_metrics['score'].mean().round(1) if not individual_metrics.empty else 0
        
        # Calculate group monthly averages
        group_monthly_scores = {}
        if len(individual_metrics) > 0 and 'monthly_scores' in individual_metrics.iloc[0]:
            # Get all months across all metrics
            all_months = set()
            for _, row in individual_metrics.iterrows():
                all_months.update(row['monthly_scores'].keys())
            
            # Calculate average for each month
            for month in all_months:
                month_scores = []
                for _, row in individual_metrics.iterrows():
                    if month in row['monthly_scores']:
                        month_scores.append(row['monthly_scores'][month])
                
                if month_scores:
                    group_monthly_scores[month] = round(sum(month_scores) / len(month_scores), 1)
    
    # Create metric cards (only for individual metrics, not the group score)
    metric_cards = []
    for _, row in group_metrics[group_metrics['is_group_score'] == False].iterrows():
        metric_cards.append(
            create_score_card(
                row['score'], 
                row['metric'], 
                monthly_scores=row['monthly_scores'],
                color_class=""
            )
        )
    
    return html.Div([
        dbc.Row([
            # Group score on the left (30%)
            dbc.Col([
                create_score_card(
                    group_score, 
                    f"{group_name}", 
                    monthly_scores=group_monthly_scores,
                    color_class="group-score"
                )
            ], width=3, className="group-score-col"),
            
            # Individual metrics on the right (70%)
            dbc.Col([
                html.Div(metric_cards, className="metric-cards-container")
            ], width=9, className="metrics-col")
        ], className="group-section mb-4")
    ])

def create_segment_layout(segment, processed_data, AVAILABLE_MONTHS, branches, appointment_types, nationalities):
    """Create the layout for a specific segment"""
    # Filter data for this segment
    df_segment = processed_data[processed_data['segment'] == segment]
    
    # Get unique groups for this segment
    groups = df_segment['group'].unique()
    
    # Create layout
    return html.Div([
        # Sticky filter container
        html.Div([
            # Filter bar
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            dbc.Row([
                                # Only show month filter for contact-center
                                dbc.Col([
                                    html.Label("Month"),
                                    dcc.Dropdown(
                                        id=f"{segment}-month-filter",
                                        options=[{"label": "Overall", "value": "Overall"}] + 
                                                [{"label": month, "value": month} for month in AVAILABLE_MONTHS],
                                        value=["Overall"],  # Default to Overall
                                        multi=True,
                                        clearable=False
                                    )
                                ], width=3),
                                # Show all filters for branch segment
                                *([
                                    dbc.Col([
                                        html.Label("Branch Name"),
                                        dcc.Dropdown(
                                            id=f"{segment}-branch-filter",
                                            options=[{"label": "Overall", "value": "Overall"}] + 
                                                    [{"label": branch, "value": branch} for branch in branches],
                                            value="Overall",
                                            clearable=False
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("Appointment Type"),
                                        dcc.Dropdown(
                                            id=f"{segment}-appointment-filter",
                                            options=[{"label": "Overall", "value": "Overall"}] + 
                                                    [{"label": apt, "value": apt} for apt in appointment_types],
                                            value="Overall",
                                            clearable=False
                                        )
                                    ], width=3),
                                    dbc.Col([
                                        html.Label("MS Nationality"),
                                        dcc.Dropdown(
                                            id=f"{segment}-nationality-filter",
                                            options=[{"label": "Overall", "value": "Overall"}] + 
                                                    [{"label": nat, "value": nat} for nat in nationalities],
                                            value="Overall",
                                            clearable=False
                                        )
                                    ], width=3)
                                ] if segment == 'branch' else [])
                            ])
                        ])
                    )
                ], width=12)
            ], className="filter-row mb-4")
        ], className="sticky-filter-container"),
        
        # Legend section with visit count
        create_legend_section(segment=segment),
        
        # Group sections
        html.Div([
            create_group_section(segment, group, df_segment) for group in groups
        ], className="group-sections-container", id=f"{segment}-groups-container")
    ], className="segment-container")

def create_legend_section(segment="branch", visit_count=0):
    """Create a hover-based legend section with visit count on the left"""
    return html.Div([
        dbc.Row([
            # Visit count on the left
            dbc.Col([
                html.P(id=f"{segment}-visit-count", children=f"Base: {visit_count} Visits", 
                       className="mt-2 font-weight-bold")
            ], width=3, className="d-flex align-items-center"),
            
            # Legend on the right
            dbc.Col([
                html.Div([
                    # Legend item 1 - Unacceptable
                    html.Div([
                        html.Div([
                            html.Span("Below 50", className="hover-legend-text text-low")
                        ], className="hover-legend-content"),
                        html.Div([
                            html.Span("Unacceptable", className="hover-legend-category"),
                            html.P("Incidence of adherence is less than 50%", className="hover-legend-description"),
                            html.P("Not close to expectations or defined practice/protocol; absolute ignorance and apathy is apparent. (immediate attention required!)", 
                                  className="hover-legend-detail")
                        ], className="hover-legend-expanded")
                    ], className="hover-legend-item"),
                    
                    # Legend item 2 - Satisfactory
                    html.Div([
                        html.Div([
                            html.Span("50-74", className="hover-legend-text text-medium")
                        ], className="hover-legend-content"),
                        html.Div([
                            html.Span("Satisfactory", className="hover-legend-category"),
                            html.P("Adherence is more than 50% but less than 3/4th", className="hover-legend-description"),
                            html.P("Ignorance apparent but apathy is not. Shows good initiative. Room for improvement (perhaps more training...)", 
                                  className="hover-legend-detail")
                        ], className="hover-legend-expanded")
                    ], className="hover-legend-item"),
                    
                    # Legend item 3 - Exemplary
                    html.Div([
                        html.Div([
                            html.Span("75+", className="hover-legend-text text-high")
                        ], className="hover-legend-content"),
                        html.Div([
                            html.Span("Exemplary", className="hover-legend-category"),
                            html.P("Adherence to best practices is at least 3 out of 4 times", className="hover-legend-description"),
                            html.P("Leads by example, an exemplary and memorable showroom experience, commendable etiquettes and a role model.", 
                                  className="hover-legend-detail")
                        ], className="hover-legend-expanded")
                    ], className="hover-legend-item")
                ], className="hover-legend")
            ], width=9)
        ])
    ], className="hover-legend-container mb-4")

