# Data Contracts

## Domain Models

### `FrameData`

Представляет один кадр видео после чтения и первичной обработки.

- `frame_index: int` порядковый номер кадра
- `timestamp_ms: float` временная отметка кадра
- `image: np.ndarray | None` матрица пикселей
- `face_detected: bool` найдено ли лицо
- `landmarks: np.ndarray | None` landmarks лица
- `quality_score: float` агрегированная оценка качества
- `quality_flags: list[str]` диагностические флаги качества

### `FacialFeatureVector`

Мимические признаки, рассчитанные для кадра.

- `eye_openness`
- `eyebrow_raise`
- `mouth_openness`
- `lip_corner_movement`
- `facial_asymmetry`
- `response_intensity`

### `StimulusDescriptor`

Описание визуального стимула, с которым связывается реакция.

- `stimulus_id`
- `description`
- `category`
- `metadata`

### `ReactionProfile`

Временной профиль реакции.

- `stimulus_id`
- `timestamps_ms`
- `features`
- `onset_ms`
- `peak_ms`
- `recovery_ms`
- `metadata`

### `NormativeProfile`

Нормативный профиль, используемый как эталон.

- `stimulus_category`
- `expected_features`
- `timestamps_ms`
- `thresholds`
- `metadata`

### `DeviationResult`

Итог измерения девиации.

- `global_score`
- `amplitude_score`
- `latency_score`
- `symmetry_score`
- `recovery_score`
- `confidence`
- `warnings`

### `AnalysisArtifacts`

Полный комплект артефактов, который возвращает pipeline.

- `stimulus`
- `normative_profile`
- `reaction_profile`
- `deviation_result`
- `frame_data`
- `feature_vectors`
- `comparison`

## JSON Report Contract

Отчет имеет следующие верхнеуровневые блоки:

- `input`
  Путь к видео и идентификатор модуля.

- `stimulus`
  Описание, идентификатор и категория стимула.

- `quality`
  Количество обработанных и валидных кадров, доля успешного трекинга.

- `normative_reference`
  Категория нормативного профиля, пороги сравнения и его метаданные.

- `reaction_profile`
  Временная шкала, признаки и ключевые точки `onset/peak/recovery`.

- `deviation`
  Компонентные и глобальный scores, а также confidence.

- `warnings`
  Текстовые предупреждения об отклонении или качестве.

- `disclaimer`
  Явное ограничение: отчет не является медицинской диагностикой.

## CSV Contract

CSV-отчет содержит по одной строке на временную точку профиля:

- `timestamp_ms`
- `eye_openness`
- `eyebrow_raise`
- `mouth_openness`
- `lip_corner_movement`
- `facial_asymmetry`
- `response_intensity`

## Нормативный профиль

Минимальный JSON нормативного профиля:

```json
{
  "stimulus_category": "positive",
  "timestamps_ms": [0, 200, 400],
  "expected_features": [
    {
      "eye_openness": 0.3,
      "eyebrow_raise": 0.1,
      "mouth_openness": 0.15,
      "lip_corner_movement": 0.05,
      "facial_asymmetry": 0.02,
      "response_intensity": 0.2
    }
  ],
  "thresholds": {
    "amplitude_tolerance": 0.15,
    "latency_tolerance_ms": 250.0,
    "symmetry_tolerance": 0.1,
    "recovery_tolerance": 0.2
  }
}
```
