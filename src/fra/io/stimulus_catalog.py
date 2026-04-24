from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from fra.domain.models import StimulusDescriptor


@dataclass
class StimulusCatalogEntry:
    stimulus_id: str
    dataset: str
    category: str
    description: str
    image_path: str
    valence_mean: float
    arousal_mean: float
    valence_sd: float | None = None
    arousal_sd: float | None = None
    metadata: dict[str, str | float | int | bool] | None = None


class DatasetStimulusCatalog:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.datasets_root = self.project_root / "datasets" / "data"

    def get_entry(
        self,
        dataset: str,
        stimulus_id: str | None = None,
        category: str | None = None,
    ) -> StimulusCatalogEntry:
        dataset_key = dataset.lower()
        entries = self._load_entries(dataset_key)
        if not entries:
            raise FileNotFoundError(f"No stimuli found for dataset: {dataset}")

        if stimulus_id:
            for entry in entries:
                if entry.stimulus_id.lower() == stimulus_id.lower():
                    return entry
            raise FileNotFoundError(f"Stimulus not found in {dataset}: {stimulus_id}")

        if category:
            filtered = [entry for entry in entries if entry.category.lower() == category.lower()]
            if filtered:
                entries = filtered

        return random.choice(entries)

    def get_descriptor(
        self,
        dataset: str,
        stimulus_id: str | None = None,
        category: str | None = None,
    ) -> StimulusDescriptor:
        entry = self.get_entry(dataset=dataset, stimulus_id=stimulus_id, category=category)
        metadata = dict(entry.metadata or {})
        metadata.update(
            {
                "image_path": entry.image_path,
                "valence_mean": entry.valence_mean,
                "arousal_mean": entry.arousal_mean,
            }
        )
        if entry.valence_sd is not None:
            metadata["valence_sd"] = entry.valence_sd
        if entry.arousal_sd is not None:
            metadata["arousal_sd"] = entry.arousal_sd

        return StimulusDescriptor(
            stimulus_id=entry.stimulus_id,
            description=entry.description,
            category=entry.category,
            source_dataset=entry.dataset,
            metadata=metadata,
        )

    def list_entries(
        self,
        dataset: str,
        category: str | None = None,
        limit: int | None = None,
    ) -> list[StimulusCatalogEntry]:
        entries = self._load_entries(dataset.lower())
        if category:
            entries = [entry for entry in entries if entry.category.lower() == category.lower()]
        entries = sorted(entries, key=lambda item: item.stimulus_id)
        if limit is not None:
            entries = entries[: max(0, limit)]
        return entries

    def _load_entries(self, dataset: str) -> list[StimulusCatalogEntry]:
        if dataset == "oasis":
            return self._load_oasis_entries()
        if dataset == "gaped":
            return self._load_gaped_entries()
        if dataset == "artemis":
            return self._load_artemis_entries()
        raise ValueError(f"Unsupported dataset: {dataset}")

    def _load_oasis_entries(self) -> list[StimulusCatalogEntry]:
        csv_path = self.datasets_root / "OASIS_database_2016" / "OASIS.csv"
        images_dir = self.datasets_root / "OASIS_database_2016" / "images"
        entries: list[StimulusCatalogEntry] = []
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                stimulus_id = row[""]
                image_path = images_dir / f"{row['Theme']}.jpg"
                if not image_path.exists():
                    continue
                category = self._classify_oasis_category(
                    float(row["Valence_mean"]),
                    float(row["Arousal_mean"]),
                )
                entries.append(
                    StimulusCatalogEntry(
                        stimulus_id=stimulus_id,
                        dataset="oasis",
                        category=category,
                        description=f"{row['Theme']} ({row['Category']})",
                        image_path=str(image_path),
                        valence_mean=float(row["Valence_mean"]),
                        arousal_mean=float(row["Arousal_mean"]),
                        valence_sd=float(row["Valence_SD"]),
                        arousal_sd=float(row["Arousal_SD"]),
                        metadata={
                            "theme": row["Theme"],
                            "source": row["Source"],
                            "stimulus_group": row["Category"],
                        },
                    )
                )
        return entries

    def _load_gaped_entries(self) -> list[StimulusCatalogEntry]:
        dataset_dir = self.datasets_root / "GAPED"
        category_specs = {
            "P": ("positive", dataset_dir / "P", dataset_dir / "P_with SD.txt"),
            "N": ("neutral", dataset_dir / "N", dataset_dir / "N_with SD.txt"),
            "A": ("negative", dataset_dir / "A", dataset_dir / "A_with SD.txt"),
            "H": ("negative", dataset_dir / "H", dataset_dir / "H_with SD.txt"),
            "Sn": ("negative", dataset_dir / "Sn", dataset_dir / "Sn_with SD.txt"),
            "Sp": ("positive", dataset_dir / "Sp", dataset_dir / "Sp_with SD.txt"),
        }
        entries: list[StimulusCatalogEntry] = []
        for code, spec in category_specs.items():
            category, image_dir, stats_path = spec
            if not image_dir.exists() or not stats_path.exists():
                continue
            entries.extend(
                self._load_gaped_stats_file(
                    dataset="gaped",
                    category=category,
                    category_code=code,
                    image_dir=image_dir,
                    stats_path=stats_path,
                )
            )
        return entries

    def _load_gaped_stats_file(
        self,
        dataset: str,
        category: str,
        category_code: str,
        image_dir: Path,
        stats_path: Path,
    ) -> list[StimulusCatalogEntry]:
        entries: list[StimulusCatalogEntry] = []
        lines = stats_path.read_text(encoding="utf-8").splitlines()
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = [part for part in line.split("\t") if part]
            if len(parts) < 5:
                continue

            image_name = parts[0].strip()
            image_path = image_dir / image_name.replace(".jpg", ".bmp")
            if not image_path.exists():
                image_path = image_dir / image_name
            if not image_path.exists():
                continue

            valence_mean = float(parts[1])
            valence_sd = self._parse_gaped_sd(parts[2])
            arousal_mean = float(parts[3])
            arousal_sd = self._parse_gaped_sd(parts[4])
            entries.append(
                StimulusCatalogEntry(
                    stimulus_id=image_name.rsplit(".", 1)[0],
                    dataset=dataset,
                    category=category,
                    description=f"{category_code} stimulus {image_name}",
                    image_path=str(image_path),
                    valence_mean=valence_mean,
                    arousal_mean=arousal_mean,
                    valence_sd=valence_sd,
                    arousal_sd=arousal_sd,
                    metadata={"gaped_category_code": category_code},
                )
            )
        return entries

    @staticmethod
    def _parse_gaped_sd(raw_value: str) -> float | None:
        stripped = raw_value.strip().strip("()")
        return float(stripped) if stripped else None

    def _load_artemis_entries(self) -> list[StimulusCatalogEntry]:
        csv_path = self.datasets_root / "artemis" / "artemis_dataset_release_v0.csv"
        wiki_art_dir = self.datasets_root / "wiki_art"
        df = pd.read_csv(csv_path)
        grouped = df.groupby(["art_style", "painting"], sort=False)
        entries: list[StimulusCatalogEntry] = []

        for (art_style, painting), group in grouped:
            image_path = wiki_art_dir / art_style / f"{painting}.jpg"
            if not image_path.exists():
                continue

            emotion_counts = group["emotion"].value_counts()
            dominant_emotion = str(emotion_counts.index[0])
            dominant_share = float(emotion_counts.iloc[0] / max(1, emotion_counts.sum()))
            category = self._classify_artemis_category(dominant_emotion)
            expected_observed = self._map_artemis_to_observed(list(emotion_counts.index[:3]))
            utterances = [
                str(item).strip()
                for item in group["utterance"].dropna().head(3).tolist()
            ]

            entries.append(
                StimulusCatalogEntry(
                    stimulus_id=painting,
                    dataset="artemis",
                    category=category,
                    description=f"{painting} ({art_style})",
                    image_path=str(image_path),
                    valence_mean=self._artemis_valence_proxy(dominant_emotion),
                    arousal_mean=self._artemis_arousal_proxy(dominant_emotion),
                    metadata={
                        "art_style": art_style,
                        "dominant_artemis_emotion": dominant_emotion,
                        "dominant_emotion_share": round(dominant_share, 4),
                        "expected_stimulus_emotions": list(emotion_counts.index[:3]),
                        "expected_observed_emotions": expected_observed,
                        "emotion_distribution": {
                            str(key): float(value / max(1, emotion_counts.sum()))
                            for key, value in emotion_counts.items()
                        },
                        "utterance_examples": utterances,
                    },
                )
            )
        return entries

    @staticmethod
    def _classify_artemis_category(dominant_emotion: str) -> str:
        if dominant_emotion in {"amusement", "contentment", "excitement", "awe"}:
            return "positive"
        if dominant_emotion in {"fear", "sadness", "disgust", "anger"}:
            return "negative"
        return "neutral"

    @staticmethod
    def _artemis_valence_proxy(dominant_emotion: str) -> float:
        positive = {"amusement": 0.82, "contentment": 0.72, "excitement": 0.85, "awe": 0.68}
        negative = {"fear": 0.20, "sadness": 0.18, "disgust": 0.12, "anger": 0.10}
        neutral = {"something else": 0.50}
        mapping = {**positive, **negative, **neutral}
        return mapping.get(dominant_emotion, 0.50) * 100.0

    @staticmethod
    def _artemis_arousal_proxy(dominant_emotion: str) -> float:
        high = {"excitement": 0.85, "fear": 0.78, "anger": 0.74, "awe": 0.72, "disgust": 0.70}
        medium = {"amusement": 0.62, "sadness": 0.38, "contentment": 0.28, "something else": 0.35}
        mapping = {**high, **medium}
        return mapping.get(dominant_emotion, 0.40) * 100.0

    @staticmethod
    def _map_artemis_to_observed(artemis_emotions: list[str]) -> list[str]:
        mapping = {
            "amusement": ["happy", "surprise"],
            "contentment": ["happy", "neutral"],
            "excitement": ["surprise", "happy"],
            "awe": ["surprise", "happy"],
            "fear": ["fear", "surprise"],
            "sadness": ["sad", "neutral"],
            "disgust": ["disgust", "angry"],
            "anger": ["angry", "disgust"],
            "something else": ["neutral", "surprise"],
        }
        observed: list[str] = []
        for emotion in artemis_emotions:
            for item in mapping.get(emotion, ["neutral"]):
                if item not in observed:
                    observed.append(item)
        return observed

    @staticmethod
    def _classify_oasis_category(valence_mean: float, arousal_mean: float) -> str:
        if valence_mean >= 5.3:
            return "positive"
        if valence_mean <= 3.7 or arousal_mean >= 4.6:
            return "negative"
        return "neutral"
