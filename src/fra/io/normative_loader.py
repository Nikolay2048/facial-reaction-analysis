from __future__ import annotations

import json
from pathlib import Path

from fra.domain.models import NormativeProfile
from fra.domain.schemas import NormativeProfileSchema


class NormativeProfileLoader:
    def load(self, normative_profile_path: str) -> NormativeProfile:
        path = Path(normative_profile_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        schema = NormativeProfileSchema.model_validate(payload)
        return NormativeProfile(
            stimulus_category=schema.stimulus_category,
            expected_features=schema.expected_features,
            timestamps_ms=schema.timestamps_ms,
            thresholds=schema.thresholds,
            metadata=dict(schema.metadata),
        )
