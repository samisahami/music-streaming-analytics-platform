import os

import pandas as pd
import plotly.express as px
import streamlit as st

from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Music Streaming Analytics",
    page_icon="🎵",
    layout="wide",
)


# =========================================================
# ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# SNOWFLAKE CONNECTION
# =========================================================

@st.cache_resource
def get_engine():
    """
    Create and cache one reusable SQLAlchemy connection engine.
    """

    required_variables = [
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        missing_text = ", ".join(missing_variables)

        raise ValueError(
            f"Missing required environment variables: {missing_text}"
        )

    return create_engine(
        URL(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
    )


# =========================================================
# DATA-LOADING FUNCTIONS
# =========================================================

@st.cache_data(ttl=600)
def load_streams():
    """
    Load the enriched stream-level dataset produced by dbt.
    """

    query = """
    SELECT *
    FROM BRONZE.INT_STREAMS_ENRICHED
    ORDER BY stream_timestamp DESC
    LIMIT 100000
    """

    streams = pd.read_sql(query, get_engine())

    streams["stream_timestamp"] = pd.to_datetime(
        streams["stream_timestamp"],
        errors="coerce",
    )

    return streams


@st.cache_data(ttl=600)
def load_user_features():
    """
    Build one row per user in Snowflake for the churn demonstration.

    The event-level CTE removes duplicate event rows introduced when
    one track is associated with multiple metadata/genre records.
    """

    query = """
    WITH event_level AS (
        SELECT
            event_id,
            user_id,
            MAX(track_id) AS track_id,
            MAX(stream_timestamp) AS stream_timestamp,
            MAX(stream_duration_seconds) AS stream_duration_seconds,
            MAX(IFF(skip_flag, 1, 0)) AS skip_flag,
            MAX(IFF(completed_flag, 1, 0)) AS completed_flag
        FROM BRONZE.INT_STREAMS_ENRICHED
        GROUP BY
            event_id,
            user_id
    ),

    event_features AS (
        SELECT
            user_id,
            COUNT(*) AS total_streams,
            AVG(stream_duration_seconds) AS avg_stream_duration_seconds,
            AVG(skip_flag) AS skip_rate,
            AVG(completed_flag) AS completion_rate,
            COUNT(DISTINCT track_id) AS unique_tracks,
            MAX(stream_timestamp) AS last_stream_timestamp
        FROM event_level
        GROUP BY user_id
    ),

    genre_features AS (
        SELECT
            user_id,
            COUNT(DISTINCT track_genre) AS unique_genres
        FROM BRONZE.INT_STREAMS_ENRICHED
        WHERE track_genre IS NOT NULL
        GROUP BY user_id
    )

    SELECT
        e.user_id,
        e.total_streams,
        e.avg_stream_duration_seconds,
        e.skip_rate,
        e.completion_rate,
        e.unique_tracks,
        COALESCE(g.unique_genres, 0) AS unique_genres,
        e.last_stream_timestamp,
        DATEDIFF(
            'day',
            e.last_stream_timestamp,
            MAX(e.last_stream_timestamp) OVER ()
        ) AS days_since_last_stream
    FROM event_features e
    LEFT JOIN genre_features g
        ON e.user_id = g.user_id
    """

    return pd.read_sql(query, get_engine())


@st.cache_data(ttl=600)
def build_ml_summary():
    """
    Create the proxy churn label, train the Random Forest model,
    and return summary outputs for the dashboard.

    days_since_last_stream creates the target label but is intentionally
    excluded from the model inputs to prevent target leakage.
    """

    user_features = load_user_features().copy()

    churn_threshold = user_features[
        "days_since_last_stream"
    ].quantile(0.85)

    user_features["churn"] = (
        user_features["days_since_last_stream"]
        >= churn_threshold
    ).astype(int)

    model_features = [
        "total_streams",
        "avg_stream_duration_seconds",
        "skip_rate",
        "completion_rate",
        "unique_tracks",
        "unique_genres",
    ]

    X = user_features[model_features]
    y = user_features["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    model_metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            zero_division=0,
        ),
    }

    feature_importance = (
        pd.DataFrame(
            {
                "feature": model_features,
                "importance": model.feature_importances_,
            }
        )
        .sort_values(
            "importance",
            ascending=True,
        )
    )

    churn_distribution = (
        user_features["churn"]
        .value_counts()
        .rename_axis("churn")
        .reset_index(name="users")
    )

    churn_distribution["status"] = churn_distribution[
        "churn"
    ].map(
        {
            0: "Active",
            1: "Churn Risk",
        }
    )

    return {
        "metrics": model_metrics,
        "feature_importance": feature_importance,
        "churn_distribution": churn_distribution,
        "threshold": churn_threshold,
        "users": len(user_features),
    }


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def calculate_percentage(part, whole):
    """
    Safely calculate a percentage.
    """

    if whole == 0:
        return 0.0

    return part / whole


def format_filter_summary(
    subscriptions,
    devices,
    genres,
    start_date,
    end_date,
):
    """
    Create a short description of the currently selected filters.
    """

    subscription_text = (
        ", ".join(subscriptions)
        if subscriptions
        else "None"
    )

    device_text = (
        ", ".join(devices)
        if devices
        else "None"
    )

    genre_text = (
        f"{len(genres)} selected"
        if genres
        else "All genres"
    )

    return (
        f"Subscriptions: {subscription_text}  •  "
        f"Devices: {device_text}  •  "
        f"Genres: {genre_text}  •  "
        f"Dates: {start_date} to {end_date}"
    )


# =========================================================
# DASHBOARD HEADER
# =========================================================

st.title("🎵 Music Streaming Analytics Dashboard")

st.markdown(

    """

    An independent portfolio project analyzing synthetic music-streaming

    behavior and public music metadata using Snowflake, dbt, Python,

    Plotly, Streamlit, and scikit-learn.

    """

)


# =========================================================
# MAIN APPLICATION
# =========================================================

try:
    streams_df = load_streams()

    if streams_df.empty:
        st.warning(
            "The enriched streaming model returned no records."
        )

        st.stop()

    streams_df = streams_df.dropna(
        subset=["stream_timestamp"]
    ).copy()

    # -----------------------------------------------------
    # SIDEBAR FILTERS
    # -----------------------------------------------------

    st.sidebar.header("Filters")

    subscription_options = sorted(
        streams_df["subscription_type"]
        .dropna()
        .unique()
        .tolist()
    )

    device_options = sorted(
        streams_df["device_type"]
        .dropna()
        .unique()
        .tolist()
    )

    genre_options = sorted(
        streams_df["track_genre"]
        .dropna()
        .unique()
        .tolist()
    )

    minimum_date = streams_df[
        "stream_timestamp"
    ].min().date()

    maximum_date = streams_df[
        "stream_timestamp"
    ].max().date()

    selected_subscriptions = st.sidebar.multiselect(
        "Subscription",
        options=subscription_options,
        default=subscription_options,
    )

    selected_devices = st.sidebar.multiselect(
        "Device",
        options=device_options,
        default=device_options,
    )

    selected_genres = st.sidebar.multiselect(
        "Genres",
        options=genre_options,
        default=[],
        placeholder="Leave blank for all genres",
        help=(
            "Leave this filter blank to include every genre. "
            "Choose one or more values to narrow the dashboard."
        ),
    )

    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
    )

    if isinstance(selected_dates, (list, tuple)):
        if len(selected_dates) == 2:
            selected_start_date = selected_dates[0]
            selected_end_date = selected_dates[1]
        else:
            selected_start_date = minimum_date
            selected_end_date = maximum_date
    else:
        selected_start_date = selected_dates
        selected_end_date = selected_dates

    st.sidebar.divider()

    st.sidebar.caption(
        "Data refreshes from Snowflake every 10 minutes."
    )

    if st.sidebar.button(
        "Clear Cached Data",
        width="stretch",
    ):
        st.cache_data.clear()
        st.rerun()

    # -----------------------------------------------------
    # APPLY FILTERS
    # -----------------------------------------------------

    filter_mask = (
        streams_df["subscription_type"].isin(
            selected_subscriptions
        )
        & streams_df["device_type"].isin(
            selected_devices
        )
        & (
            streams_df["stream_timestamp"].dt.date
            >= selected_start_date
        )
        & (
            streams_df["stream_timestamp"].dt.date
            <= selected_end_date
        )
    )

    if selected_genres:
        filter_mask &= streams_df["track_genre"].isin(
            selected_genres
        )

    filtered_df = streams_df[
        filter_mask
    ].copy()

    if filtered_df.empty:
        st.warning(
            "No stream events match the selected filters. "
            "Adjust the subscription, device, genre, or date selections."
        )

        st.stop()

    # A track may have multiple genre records.
    # Keep one row per event for primary KPIs and behavior charts.
    event_df = (
        filtered_df
        .sort_values("stream_timestamp")
        .drop_duplicates(
            subset=["event_id"],
            keep="first",
        )
        .copy()
    )

    # Keep one event-genre combination for genre-based analysis.
    genre_event_df = (
        filtered_df
        .drop_duplicates(
            subset=[
                "event_id",
                "track_genre",
            ]
        )
        .copy()
    )

    # -----------------------------------------------------
    # FILTER SUMMARY
    # -----------------------------------------------------

    st.caption(
        format_filter_summary(
            selected_subscriptions,
            selected_devices,
            selected_genres,
            selected_start_date,
            selected_end_date,
        )
    )

    # -----------------------------------------------------
    # DYNAMIC KPI CARDS
    # -----------------------------------------------------

    total_streams = event_df["event_id"].nunique()

    unique_users = event_df["user_id"].nunique()

    avg_stream_duration = event_df[
        "stream_duration_seconds"
    ].mean()

    completion_rate = event_df[
        "completed_flag"
    ].astype(float).mean()

    skip_rate = event_df[
        "skip_flag"
    ].astype(float).mean()

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    kpi_col1.metric(
        "Total Streams",
        f"{total_streams:,}",
    )

    kpi_col2.metric(
        "Unique Users",
        f"{unique_users:,}",
    )

    kpi_col3.metric(
        "Average Stream Duration",
        f"{avg_stream_duration:.1f} sec",
    )

    kpi_col4.metric(
        "Completion Rate",
        f"{completion_rate:.1%}",
    )

    st.success("Connected to Snowflake successfully.")

    # -----------------------------------------------------
    # EXECUTIVE INSIGHTS
    # -----------------------------------------------------

    st.divider()
    st.subheader("📌 Executive Insights")

    device_distribution = (
        event_df["device_type"]
        .value_counts()
    )

    top_device = device_distribution.index[0]

    top_device_share = calculate_percentage(
        device_distribution.iloc[0],
        total_streams,
    )

    premium_duration = event_df.loc[
        event_df["subscription_type"] == "Premium",
        "stream_duration_seconds",
    ].mean()

    free_duration = event_df.loc[
        event_df["subscription_type"] == "Free",
        "stream_duration_seconds",
    ].mean()

    genre_completion_summary = (
        genre_event_df
        .dropna(subset=["track_genre"])
        .groupby("track_genre")
        .agg(
            completion_rate=(
                "completed_flag",
                "mean",
            ),
            streams=(
                "event_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    minimum_genre_streams = max(
        100,
        int(total_streams * 0.001),
    )

    qualified_genres = genre_completion_summary[
        genre_completion_summary["streams"]
        >= minimum_genre_streams
    ]

    if qualified_genres.empty:
        qualified_genres = genre_completion_summary

    top_completion_row = (
        qualified_genres
        .sort_values(
            "completion_rate",
            ascending=False,
        )
        .iloc[0]
    )

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.info(
            f"**{top_device}** accounts for "
            f"**{top_device_share:.1%}** of filtered streams."
        )

        st.info(
            f"The current selections include "
            f"**{total_streams:,} distinct stream events** "
            f"from **{unique_users:,} users**."
        )

    with insight_col2:
        if (
            pd.notna(premium_duration)
            and pd.notna(free_duration)
            and free_duration != 0
        ):
            premium_difference = (
                premium_duration - free_duration
            ) / free_duration

            direction = (
                "longer"
                if premium_difference >= 0
                else "shorter"
            )

            st.info(
                f"Premium listening sessions average "
                f"**{abs(premium_difference):.1%} {direction}** "
                f"than Free sessions."
            )

        else:
            st.info(
                "Select both Free and Premium subscriptions "
                "to compare average listening duration."
            )

        st.info(
            f"**{top_completion_row['track_genre']}** "
            f"has the highest qualified completion rate at "
            f"**{top_completion_row['completion_rate']:.1%}**."
        )

    # -----------------------------------------------------
    # STREAMING TRENDS
    # -----------------------------------------------------

    st.divider()
    st.subheader("📈 Streaming Trends")

    event_df["stream_month"] = (
        event_df["stream_timestamp"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_streams = (
        event_df
        .groupby("stream_month")
        .agg(
            streams=(
                "event_id",
                "nunique",
            ),
            unique_users=(
                "user_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    trend_fig = px.line(
        monthly_streams,
        x="stream_month",
        y="streams",
        markers=True,
        title="Monthly Stream Activity",
        labels={
            "stream_month": "Month",
            "streams": "Distinct Streams",
        },
    )

    trend_fig.update_traces(
        hovertemplate=(
            "<b>%{x|%B %Y}</b><br>"
            "Streams: %{y:,.0f}"
            "<extra></extra>"
        )
    )

    trend_fig.update_layout(
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        trend_fig,
        width="stretch",
    )

    # -----------------------------------------------------
    # AUDIENCE MIX
    # -----------------------------------------------------

    st.divider()
    st.subheader("👥 Audience and Device Mix")

    mix_col1, mix_col2 = st.columns(2)

    subscription_counts = (
        event_df["subscription_type"]
        .dropna()
        .value_counts()
        .rename_axis("subscription_type")
        .reset_index(name="streams")
    )

    subscription_fig = px.pie(
        subscription_counts,
        names="subscription_type",
        values="streams",
        title="Streams by Subscription",
        hole=0.48,
    )

    subscription_fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Streams: %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    subscription_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        legend_title_text="Subscription",
    )

    mix_col1.plotly_chart(
        subscription_fig,
        width="stretch",
    )

    device_counts = (
        event_df["device_type"]
        .dropna()
        .value_counts()
        .rename_axis("device_type")
        .reset_index(name="streams")
    )

    device_fig = px.pie(
        device_counts,
        names="device_type",
        values="streams",
        title="Streams by Device",
        hole=0.48,
    )

    device_fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Streams: %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    device_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        legend_title_text="Device",
    )

    mix_col2.plotly_chart(
        device_fig,
        width="stretch",
    )

    # -----------------------------------------------------
    # CONTENT ANALYSIS
    # -----------------------------------------------------

    st.divider()
    st.subheader("🎼 Content Performance")

    content_col1, content_col2 = st.columns(2)

    genre_counts = (
        genre_event_df["track_genre"]
        .dropna()
        .value_counts()
        .head(15)
        .rename_axis("track_genre")
        .reset_index(name="streams")
    )

    genre_fig = px.bar(
        genre_counts,
        x="streams",
        y="track_genre",
        orientation="h",
        title="Top 15 Genres by Streams",
        labels={
            "streams": "Distinct Stream Events",
            "track_genre": "Genre",
        },
    )

    genre_fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        },
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    genre_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Streams: %{x:,.0f}"
            "<extra></extra>"
        )
    )

    content_col1.plotly_chart(
        genre_fig,
        width="stretch",
    )

    completion_by_genre = (
        genre_completion_summary
        .sort_values(
            [
                "streams",
                "completion_rate",
            ],
            ascending=False,
        )
        .head(15)
        .sort_values(
            "completion_rate",
            ascending=True,
        )
    )

    completion_genre_fig = px.bar(
        completion_by_genre,
        x="completion_rate",
        y="track_genre",
        orientation="h",
        title="Completion Rate for High-Volume Genres",
        labels={
            "completion_rate": "Completion Rate",
            "track_genre": "Genre",
        },
        hover_data={
            "streams": ":,",
            "completion_rate": ":.1%",
        },
    )

    completion_genre_fig.update_xaxes(
        tickformat=".0%",
    )

    completion_genre_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    content_col2.plotly_chart(
        completion_genre_fig,
        width="stretch",
    )

    # -----------------------------------------------------
    # LISTENING BEHAVIOR
    # -----------------------------------------------------

    st.divider()
    st.subheader("🎧 Listening Behavior")

    behavior_col1, behavior_col2 = st.columns(2)

    duration_by_device = (
        event_df
        .groupby("device_type")
        .agg(
            avg_duration=(
                "stream_duration_seconds",
                "mean",
            ),
            streams=(
                "event_id",
                "nunique",
            ),
        )
        .reset_index()
        .sort_values(
            "avg_duration",
            ascending=True,
        )
    )

    duration_device_fig = px.bar(
        duration_by_device,
        x="avg_duration",
        y="device_type",
        orientation="h",
        title="Average Stream Duration by Device",
        labels={
            "avg_duration": "Average Seconds",
            "device_type": "Device",
        },
        hover_data={
            "streams": ":,",
            "avg_duration": ":.1f",
        },
    )

    duration_device_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    behavior_col1.plotly_chart(
        duration_device_fig,
        width="stretch",
    )

    rate_comparison = pd.DataFrame(
        {
            "metric": [
                "Completion Rate",
                "Skip Rate",
            ],
            "rate": [
                completion_rate,
                skip_rate,
            ],
        }
    )

    rate_fig = px.bar(
        rate_comparison,
        x="metric",
        y="rate",
        title="Completion and Skip Rates",
        labels={
            "metric": "Behavior Metric",
            "rate": "Rate",
        },
        text_auto=".1%",
    )

    rate_fig.update_yaxes(
        tickformat=".0%",
        range=[0, 1],
    )

    rate_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    behavior_col2.plotly_chart(
        rate_fig,
        width="stretch",
    )

    # -----------------------------------------------------
    # MACHINE LEARNING / CHURN ANALYTICS
    # -----------------------------------------------------

    st.divider()
    st.subheader("🤖 Churn-Risk Modeling")

    st.caption(
        "This section uses the overall user population rather than "
        "the active dashboard filters. Because the source data is "
        "synthetic and contains no true cancellation records, churn "
        "is represented by a transparent inactivity-based proxy."
    )

    ml_summary = build_ml_summary()

    model_metrics = ml_summary["metrics"]

    ml_metric_col1, ml_metric_col2, ml_metric_col3, ml_metric_col4 = (
        st.columns(4)
    )

    ml_metric_col1.metric(
        "Model Accuracy",
        f"{model_metrics['accuracy']:.1%}",
    )

    ml_metric_col2.metric(
        "Churn Precision",
        f"{model_metrics['precision']:.1%}",
    )

    ml_metric_col3.metric(
        "Churn Recall",
        f"{model_metrics['recall']:.1%}",
    )

    ml_metric_col4.metric(
        "Churn F1 Score",
        f"{model_metrics['f1']:.1%}",
    )

    ml_col1, ml_col2 = st.columns(2)

    churn_fig = px.pie(
        ml_summary["churn_distribution"],
        names="status",
        values="users",
        title="Proxy Churn-Risk Distribution",
        hole=0.48,
    )

    churn_fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Users: %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    churn_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    ml_col1.plotly_chart(
        churn_fig,
        width="stretch",
    )

    importance_fig = px.bar(
        ml_summary["feature_importance"],
        x="importance",
        y="feature",
        orientation="h",
        title="Random Forest Feature Importance",
        labels={
            "importance": "Importance",
            "feature": "Feature",
        },
    )

    importance_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    importance_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Importance: %{x:.3f}"
            "<extra></extra>"
        )
    )

    ml_col2.plotly_chart(
        importance_fig,
        width="stretch",
    )

    with st.expander("ℹ️ Churn Model Methodology"):
        st.markdown(
            f"""
            - The source data contains no true cancellation event.
            - The churn proxy labels users in the highest inactivity
              group using an **85th-percentile recency threshold**.
            - The resulting inactivity threshold is approximately
              **{ml_summary['threshold']:.1f} days**.
            - `days_since_last_stream` creates the label but is excluded
              from model training to prevent target leakage.
            - The model uses streaming frequency, duration, skip rate,
              completion rate, track diversity, and genre diversity.
            - Low churn recall indicates that the remaining synthetic
              behavior features contain limited predictive signal.
            """
        )

    # -----------------------------------------------------
    # CORRELATION ANALYSIS
    # -----------------------------------------------------

    st.divider()
    st.subheader("🔗 Behavioral Correlations")

    filtered_user_features = (
        event_df
        .groupby("user_id")
        .agg(
            total_streams=(
                "event_id",
                "nunique",
            ),
            avg_duration=(
                "stream_duration_seconds",
                "mean",
            ),
            skip_rate=(
                "skip_flag",
                "mean",
            ),
            completion_rate=(
                "completed_flag",
                "mean",
            ),
            unique_tracks=(
                "track_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    correlation_columns = [
        "total_streams",
        "avg_duration",
        "skip_rate",
        "completion_rate",
        "unique_tracks",
    ]

    correlation_matrix = (
        filtered_user_features[
            correlation_columns
        ]
        .corr()
        .round(2)
    )

    correlation_fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        title="User-Level Behavioral Correlation Matrix",
        labels={
            "x": "Feature",
            "y": "Feature",
            "color": "Correlation",
        },
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu_r",
    )

    correlation_fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        correlation_fig,
        width="stretch",
    )

    st.caption(
        "Correlation describes association, not causation. "
        "Values close to 1 indicate a positive relationship, "
        "values close to -1 indicate a negative relationship, "
        "and values close to 0 indicate little linear relationship."
    )

    # -----------------------------------------------------
    # DATASET PREVIEW
    # -----------------------------------------------------

    st.divider()

    with st.expander("📋 View Filtered Dataset Preview"):
        st.caption(
            f"Showing the first 100 rows from "
            f"{len(filtered_df):,} filtered enriched records. "
            f"These represent {total_streams:,} distinct stream events."
        )

        preview_columns = [
            "event_id",
            "user_id",
            "track_id",
            "track_name",
            "artists",
            "album_name",
            "track_genre",
            "stream_timestamp",
            "device_type",
            "subscription_type",
            "stream_duration_seconds",
            "skip_flag",
            "completed_flag",
        ]

        available_preview_columns = [
            column
            for column in preview_columns
            if column in filtered_df.columns
        ]

        st.dataframe(
            filtered_df[
                available_preview_columns
            ].head(100),
            width="stretch",
            hide_index=True,
        )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    st.divider()

    st.caption(
        "Built with Python, Snowflake, dbt, Streamlit, Plotly, "
        "SQLAlchemy, and scikit-learn."
    )


except Exception as exc:
    st.error(
        "Unable to load or process dashboard data."
    )

    st.exception(exc)