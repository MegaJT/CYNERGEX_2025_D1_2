from dash import Input, Output
from data_loader import filter_data, prepare_dashboard_data
from layout_components import create_segment_layout, create_group_section


def register_callbacks(app):
    """Register all callbacks for the application

    This version uses pre-filtered data from app.user_data instead of raw dataframes
    """

    # Callback to update content based on selected tab
    @app.callback(
        Output("segment-content", "children"),
        Output("current-segment", "data"),
        [Input("segment-tabs", "active_tab"), Input("user-id", "data")],
    )
    def render_segment_content(active_tab, user_id):
        if active_tab and user_id in app.user_data:
            user_data = app.user_data[user_id]
            segment_data = user_data[active_tab]

            # Get unique values for filters based on segment
            if active_tab == "branch":
                branches = segment_data["branches"]
                appointment_types = segment_data["appointment_types"]
                nationalities = segment_data["nationalities"]
                sc_names = segment_data["sc_names"]
                available_months = segment_data["months"]
            else:
                # For other segments, use their own SC names
                branches = ["Overall"]
                appointment_types = ["Overall"]
                nationalities = ["Overall"]
                sc_names = app.user_data[user_id]["branch"][
                    "sc_names"
                ]  # Use branch SC names for all segments
                available_months = segment_data["months"]

            return (
                create_segment_layout(
                    active_tab,
                    user_data["combined_processed"],
                    available_months,
                    branches,
                    appointment_types,
                    nationalities,
                    sc_names,
                ),
                active_tab,
            )
        return "Select a segment to view data.", "branch"

    # Add callback for month filter validation
    for segment in [
        "branch",
        "contact-centre",
        "website",
        "social-media",
        "combined-contact-centre",
    ]:

        @app.callback(
            Output(f"{segment}-month-filter", "value"),
            Input(f"{segment}-month-filter", "value"),
        )
        def validate_month_selection(selected_months, segment=segment):
            if not selected_months:  # If no months are selected
                return ["Overall"]  # Default to Overall
            return selected_months

    @app.callback(
        Output("branch-groups-container", "children"),
        Output("branch-visit-count", "children"),
        [
            Input("branch-branch-filter", "value"),
            Input("branch-appointment-filter", "value"),
            Input("branch-month-filter", "value"),
            Input("branch-nationality-filter", "value"),
            Input("branch-sc-filter", "value"),
            Input("user-id", "data"),
            Input("trend-toggle", "value"),
        ],
    )
    def update_branch_content(
        branch, appointment_type, month, nationality, sc_name, user_id, trend_mode
    ):
        if user_id not in app.user_data:
            return [], "Base: 0 Visits"

        # Get pre-filtered data for this user
        branch_df = app.user_data[user_id]["branch"]["df"]
        branch_available_months = app.user_data[user_id]["branch"]["months"]

        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(
            branch_df, branch, appointment_type, month, nationality, sc_name
        )

        # Update visit count
        visit_count = len(filtered_raw_df)

        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(
            filtered_raw_df, branch_available_months, "branch"
        )

        # Get the branch segment data
        df_segment = filtered_processed_data[
            filtered_processed_data["segment"] == "branch"
        ]

        # Get unique groups
        groups = df_segment["group"].unique()

        # Create updated group sections
        updated_group_sections = [
            create_group_section("branch", group, df_segment, trend_mode=trend_mode)
            for group in groups
        ]

        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for contact-centre segment
    @app.callback(
        Output("contact-centre-groups-container", "children"),
        Output("contact-centre-visit-count", "children"),
        [
            Input("contact-centre-month-filter", "value"),
            Input("contact-centre-sc-filter", "value"),
            Input("user-id", "data"),
            Input("trend-toggle", "value"),
        ],
    )
    def update_contact_centre_content(month, sc_name, user_id, trend_mode):
        if user_id not in app.user_data:
            return [], "Base: 0 Visits"

        # Get pre-filtered data for this user
        contact_centre_df = app.user_data[user_id]["contact-centre"]["df"]
        contact_centre_available_months = app.user_data[user_id]["contact-centre"][
            "months"
        ]

        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(
            contact_centre_df, "Overall", "Overall", month, "Overall", sc_name
        )

        # Update visit count
        visit_count = len(filtered_raw_df)

        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(
            filtered_raw_df, contact_centre_available_months, "contact-centre"
        )

        # Get the contact-centre segment data
        df_segment = filtered_processed_data[
            filtered_processed_data["segment"] == "contact-centre"
        ]

        # Get unique groups
        groups = df_segment["group"].unique()

        # Create updated group sections
        updated_group_sections = [
            create_group_section(
                "contact-centre", group, df_segment, trend_mode=trend_mode
            )
            for group in groups
        ]

        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for website segment
    @app.callback(
        Output("website-groups-container", "children"),
        Output("website-visit-count", "children"),
        [
            Input("website-month-filter", "value"),
            Input("website-sc-filter", "value"),
            Input("user-id", "data"),
            Input("trend-toggle", "value"),
        ],
    )
    def update_website_content(month, sc_name, user_id, trend_mode):
        if user_id not in app.user_data:
            return [], "Base: 0 Visits"

        # Get pre-filtered data for this user
        website_df = app.user_data[user_id]["website"]["df"]
        website_available_months = app.user_data[user_id]["website"]["months"]

        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(
            website_df, "Overall", "Overall", month, "Overall", sc_name
        )

        # Update visit count
        visit_count = len(filtered_raw_df)

        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(
            filtered_raw_df, website_available_months, "website"
        )

        # Get the website segment data
        df_segment = filtered_processed_data[
            filtered_processed_data["segment"] == "website"
        ]

        # Get unique groups
        groups = df_segment["group"].unique()

        # Create updated group sections
        updated_group_sections = [
            create_group_section("website", group, df_segment, trend_mode=trend_mode)
            for group in groups
        ]

        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for social-media segment
    @app.callback(
        Output("social-media-groups-container", "children"),
        Output("social-media-visit-count", "children"),
        [
            Input("social-media-month-filter", "value"),
            Input("social-media-sc-filter", "value"),
            Input("user-id", "data"),
            Input("trend-toggle", "value"),
        ],
    )
    def update_social_media_content(month, sc_name, user_id, trend_mode):
        if user_id not in app.user_data:
            return [], "Base: 0 Visits"

        # Get pre-filtered data for this user
        social_media_df = app.user_data[user_id]["social-media"]["df"]
        social_media_available_months = app.user_data[user_id]["social-media"]["months"]

        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(
            social_media_df, "Overall", "Overall", month, "Overall", sc_name
        )

        # Update visit count
        visit_count = len(filtered_raw_df)

        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(
            filtered_raw_df, social_media_available_months, "social-media"
        )

        # Get the social-media segment data
        df_segment = filtered_processed_data[
            filtered_processed_data["segment"] == "social-media"
        ]

        # Get unique groups
        groups = df_segment["group"].unique()

        # Create updated group sections
        updated_group_sections = [
            create_group_section(
                "social-media", group, df_segment, trend_mode=trend_mode
            )
            for group in groups
        ]

        return updated_group_sections, f"Base: {visit_count} Visits"

    # Callback for combined-contact-centre segment
    @app.callback(
        Output("combined-contact-centre-groups-container", "children"),
        Output("combined-contact-centre-visit-count", "children"),
        [
            Input("combined-contact-centre-month-filter", "value"),
            Input("combined-contact-centre-sc-filter", "value"),
            Input("user-id", "data"),
            Input("trend-toggle", "value"),
        ],
    )
    def combined_update_contact_centre_content(month, sc_name, user_id, trend_mode):
        if user_id not in app.user_data:
            return [], "Base: 0 Visits"

        # Get pre-filtered data for this user
        combined_contact_centre_df = app.user_data[user_id]["combined-contact-centre"][
            "df"
        ]
        combined_contact_centre_available_months = app.user_data[user_id][
            "combined-contact-centre"
        ]["months"]

        # Filter the raw dataframe based on selections
        filtered_raw_df = filter_data(
            combined_contact_centre_df, "Overall", "Overall", month, "Overall", sc_name
        )

        # Update visit count
        visit_count = len(filtered_raw_df)

        # Recalculate the metrics based on the filtered data
        filtered_processed_data = prepare_dashboard_data(
            filtered_raw_df,
            combined_contact_centre_available_months,
            "combined-contact-centre",
        )

        # Get the contact-centre segment data
        df_segment = filtered_processed_data[
            filtered_processed_data["segment"] == "combined-contact-centre"
        ]

        # Get unique groups
        groups = df_segment["group"].unique()

        # Create updated group sections
        updated_group_sections = [
            create_group_section(
                "combined-contact-centre", group, df_segment, trend_mode=trend_mode
            )
            for group in groups
        ]

        return updated_group_sections, f"Base: {visit_count} Visits"
