from __future__ import annotations

import pandas as pd

from fra.domain.models import ReactionProfile


class CSVReportBuilder:
    def build(self, reaction_profile: ReactionProfile) -> pd.DataFrame:
        rows = []
        for timestamp_ms, feature_map in zip(reaction_profile.timestamps_ms, reaction_profile.features):
            rows.append({"timestamp_ms": timestamp_ms, **feature_map})
        return pd.DataFrame(rows)

    def build_from_report(self, payload: dict) -> pd.DataFrame:
        profile = payload.get("reaction_profile", {})
        timestamps = profile.get("timestamps_ms", [])
        features = profile.get("features", [])
        rows = []
        for timestamp_ms, feature_map in zip(timestamps, features):
            rows.append({"timestamp_ms": timestamp_ms, **feature_map})
        return pd.DataFrame(rows)
