# Star Schema Design

## Dimension Tables

| Table | Grain | Purpose |
|--------|-------|---------|
| dim_users | One row per user | User demographics and profile information |
| dim_tracks | One row per track | Track metadata |
| dim_artists | One row per artist | Artist metadata |
| dim_albums | One row per album | Album metadata |
| dim_devices | One row per device | Device information |
| dim_subscription | One row per subscription | Subscription plan details |
| dim_date | One row per calendar date | Date dimension |

---

## Fact Tables

| Table | Grain | Purpose |
|--------|-------|---------|
| fact_listening_events | One row per listening event | Playback analytics |
| fact_search_events | One row per search | Search analytics |
| fact_playlist_events | One row per playlist event | Playlist interactions |
| fact_payment_events | One row per payment | Revenue analytics |
| fact_recommendation_events | One row per recommendation interaction | Recommendation performance |

---

## Business Marts

- mart_user_engagement
- mart_subscription_metrics
- mart_track_performance
- mart_artist_performance
- mart_revenue
- mart_retention
- mart_recommendation_metrics

---

## Machine Learning Feature Tables

- feature_user_behavior_30d
- feature_churn_prediction
- feature_playlist_preferences
- feature_recommendation_training