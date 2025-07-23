# -*- coding: utf-8 -*-
"""Generate spatiotemporal maps of global attitudes toward the dual-carbon goal
using GDELT event data and TimeMapper.

This script queries the GDELT Events database for articles mentioning carbon
neutrality or related concepts, creates a CSV compatible with the TimeMapper
web tool and also exports a KML file for viewing in Google Earth.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import List

import pandas as pd
from gdelt import gdelt as gd
import simplekml


KEYWORDS = [
    "carbon neutral",
    "net zero",
    "carbon emissions",
    "碳中和",
    "碳達峰",
    "碳达峰",
    "climate change",
]


def fetch_events(start: datetime, end: datetime) -> pd.DataFrame:
    """Fetch events from GDELT within the date range."""
    g = gd()
    df_list: List[pd.DataFrame] = []
    current = start
    while current <= end:
        # GDELT expects date strings like 'YYYY MM DD'
        date_str = current.strftime("%Y %m %d")
        try:
            data = g.Search([date_str], table="events", coverage=False)
            df_list.append(data)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to fetch {date_str}: {exc}")
        current += timedelta(days=1)
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()


def filter_events(df: pd.DataFrame) -> pd.DataFrame:
    """Filter events mentioning carbon-related keywords."""
    pattern = re.compile("|".join(KEYWORDS), re.IGNORECASE)
    mask = (
        df["SOURCEURL"].fillna("").str.contains(pattern)
        | df["Actor1Name"].fillna("").str.contains(pattern)
        | df["Actor2Name"].fillna("").str.contains(pattern)
        | df.get("CAMEOCodeDescription", pd.Series(["" for _ in range(len(df))])).fillna("").str.contains(pattern)
    )
    return df[mask].copy()


def to_timemapper_csv(df: pd.DataFrame, csv_path: str) -> None:
    """Export events to a CSV that can be loaded in TimeMapper."""
    rows = []
    for _, row in df.iterrows():
        date = datetime.strptime(str(row["SQLDATE"]), "%Y%m%d").strftime("%Y-%m-%d")
        title = row.get("Actor1Name") or "Event"
        desc = row.get("SOURCEURL", "")
        rows.append({
            "title": title,
            "description": desc,
            "start_date": date,
            "end_date": "",
            "latitude": row.get("ActionGeo_Lat"),
            "longitude": row.get("ActionGeo_Long"),
        })
    out_df = pd.DataFrame(rows)
    out_df.to_csv(csv_path, index=False)


def to_kml(df: pd.DataFrame, kml_path: str) -> None:
    """Create a KML file from the events."""
    kml = simplekml.Kml()
    for _, row in df.iterrows():
        name = row.get("Actor1Name") or "Event"
        description = row.get("SOURCEURL", "")
        lat = row.get("ActionGeo_Lat")
        lon = row.get("ActionGeo_Long")
        if lat is None or lon is None:
            continue
        pnt = kml.newpoint(name=name, description=description)
        pnt.coords = [(lon, lat)]
        try:
            dt = datetime.strptime(str(row["SQLDATE"]), "%Y%m%d")
            pnt.timestamp.when = dt.isoformat()
        except Exception:  # noqa: BLE001
            pass
    kml.save(kml_path)


def main() -> None:
    start = datetime.strptime(os.getenv("START_DATE", "2025-07-20"), "%Y-%m-%d")
    end = datetime.strptime(os.getenv("END_DATE", "2025-07-22"), "%Y-%m-%d")
    events = fetch_events(start, end)
    if events.empty:
        print("No data downloaded")
        return
    filtered = filter_events(events)
    if filtered.empty:
        print("No carbon-related events found")
        return
    csv_path = "carbon_timemapper.csv"
    kml_path = "carbon_events.kml"
    to_timemapper_csv(filtered, csv_path)
    to_kml(filtered, kml_path)
    print(f"Wrote {len(filtered)} events to {csv_path} and {kml_path}")


if __name__ == "__main__":
    main()
