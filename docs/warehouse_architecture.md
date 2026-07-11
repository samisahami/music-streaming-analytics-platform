# Warehouse Architecture

## Data Sources

### Public Reference Data

- Artists
- Albums
- Tracks
- Genre
- Audio Metadata

## Generated Event Data

- Listening Events
- Sessions
- Seaches
- Playlist Activity-
- Likes
- Recommended Events
- Subscription Events
- Payments

## Medallion Architecture

### Bronze Layer

Purpose:

Store raw immutable data exactly as received.

Charateristics:

- No business logic
- Append-only 
- Historical record
- Landing zone

--- 