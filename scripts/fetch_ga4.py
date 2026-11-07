import json, os
from datetime import datetime, timedelta, timezone
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric, FilterExpression, Filter
from pathlib import Path

property_id = os.environ["GA4_PROPERTY_ID"].strip()
client = BetaAnalyticsDataClient()
request = RunReportRequest(
    property=f"properties/{property_id}",
    date_ranges=[DateRange(start_date="89daysAgo", end_date="today")],
    dimensions=[Dimension(name="date"), Dimension(name="pagePath")],
    metrics=[Metric(name="eventCount")],
    dimension_filter=FilterExpression(filter=Filter(field_name="eventName", string_filter=Filter.StringFilter(value="sns_redirect", match_type=Filter.StringFilter.MatchType.EXACT))),
    limit=10000,
)
response = client.run_report(request)
today = datetime.now(timezone(timedelta(hours=9))).date()
days = {(today - timedelta(days=i)).isoformat(): {"date": (today - timedelta(days=i)).isoformat(), "instagram": 0, "tiktok": 0} for i in range(90)}
for row in response.rows:
    date, path = (v.value for v in row.dimension_values)
    date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    if date not in days:
        continue
    if path.rstrip("/") == "/instagram":
        platform = "instagram"
    elif path.rstrip("/") == "/tiktok":
        platform = "tiktok"
    else:
        continue
    days[date][platform] += int(row.metric_values[0].value)
out = {"updatedAt": datetime.now(timezone.utc).isoformat(), "days": [days[k] for k in sorted(days)]}
Path("dashboard/data.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print("Saved", len(out["days"]), "days")
