# Logical Data Model

## Dimension Tables

### dim_users

**Grain**

One row represents one user.

---

### dim_artists

**Grain**

One row represents one artist.

---

### dim_albums

**Grain**

One row represents one album.

---

### dim_tracks

**Grain**

One row represents one track.

---

### dim_devices

**Grain**

One row represents one device type.

---

### dim_subscription

**Grain**

One row represents one subscription.

---

## Fact Tables

### fact_listening_events

**Grain**

One row represents one listening event.

---

### fact_search_events

**Grain**

One row represents one search performed.

---

### fact_playlist_events

**Grain**

One row represents one playlist action.

---

### fact_payment_events

**Grain**

One row represents one payment transaction.

---

### fact_recommendation_events

**Grain**

One row represents one recommendation impression or interaction.