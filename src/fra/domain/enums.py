from enum import Enum


class StimulusType(str, Enum):
    GENERIC = "generic"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ReportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class QualityFlag(str, Enum):
    NO_FACE = "no_face"
    LOW_BRIGHTNESS = "low_brightness"
    LOW_SHARPNESS = "low_sharpness"
    PARTIAL_OCCLUSION = "partial_occlusion"
