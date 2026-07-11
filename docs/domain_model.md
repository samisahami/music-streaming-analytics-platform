# Domain Model

## Core Business Entities

- Users
- Artists
- Albums
- Tracks
- Listening Events
- Sessions
- Playlists
- Devices
- Subscriptions
- Payments
- Searches
- Likes
- Recommendations

---

## Event-Driven Architecture

The platform models user interactions as business events. Each user action generates an event that can be analyzed downstream.

Examples include:

- Track Played
- Track Completed
- Track Skipped
- Search Performed
- Playlist Created
- Playlist Updated
- Recommendation Viewed
- Recommendation Clicked
- Subscription Started
- Subscription Cancelled
- Payment Processed

---

## Entity Categories

Reference Data
- Artists
- Albums
- Tracks
- Genres

Master Data
- Users
- Devices
- Subscriptions

Transactional / Event Data
- Listening Events
- Searches
- Likes
- Payments
- Playlist Activity
- Recommendation Events