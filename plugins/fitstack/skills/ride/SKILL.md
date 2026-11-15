---
name: ride
description: Analyze the user's recent bike rides and recommend the next ride — long endurance ride, easy spin, or intervals — building toward their long-ride goal. Use when the user asks about cycling, a ride they did, or what ride to do next.
---

# Ride

Follows [skill-format](../../reference/skill-format.md): inputs, analysis,
recommendation. Gather focus: "rides".

## Analysis

- Longest ride, weekly ride time `(calc)`, and average speed and heart rate trend.
- Compare against this month's ride milestone.
- How past ride plans went (`outcome` records).

## Recommendation

- **Long ride (usually weekend):** about 10–20% longer than the last long ride, steady
  conversational effort. Indoors is fine in bad weather.
- **Easy spin:** 30–60 min very easy, good the day after a hard leg day.
- **Rides of 2 hours or more:** fuel about every 30–45 minutes (carbs) and drink
  regularly. Put this in `NOTES`.
- No long ride the day before or after a long run or a heavy leg day.
