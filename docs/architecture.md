# Architecture

## Назначение

Проект реализует аналитический CV-модуль для оценки отклонения мимической реакции человека на визуальный стимул. Система принимает:

- видео реакции;
- текстовое описание визуального стимула;
- нормативный временной профиль реакции.

На выходе формируется:

- временной профиль реакции;
- интегральный показатель девиации;
- показатель доверия к измерению;
- JSON/CSV-отчет.

## Слои

- `fra.cli`
  Отвечает за CLI и сценарии запуска `analyze`, `validate-profile`, `export-report`.

- `fra.api`
  Оркестрация пайплайна. Здесь нет низкоуровневой логики CV; только последовательность шагов и передача артефактов между слоями.

- `fra.io`
  Граница с внешними источниками данных: видео, stimulus description, normative profile, итоговые отчеты.

- `fra.vision`
  Детекция и трекинг лица, извлечение landmarks, оценка качества кадров.

- `fra.features`
  Преобразование landmarks в интерпретируемые признаки и их нормализация по времени.

- `fra.profiling`
  Построение временного профиля реакции и его синхронизация с нормативной кривой.

- `fra.scoring`
  Сравнение наблюдаемой реакции с нормативом и расчет девиации.

- `fra.reports`
  Сериализация результата в человеко- и машинно-читаемую форму.

- `fra.domain`
  Единые доменные сущности, которыми обмениваются все слои.

## Структура файлов

### Точка входа

- `src/fra/main.py`
  Запуск CLI и маршрутизация команд.

- `src/fra/cli.py`
  Определение аргументов командной строки.

### Оркестрация

- `src/fra/api/pipeline.py`
  Главный сценарий анализа. Собирает зависимые сервисы, выполняет шаги пайплайна и возвращает `AnalysisArtifacts`.

### Доменные модели

- `src/fra/domain/models.py`
  Dataclass-модели: `FrameData`, `FacialFeatureVector`, `StimulusDescriptor`, `ReactionProfile`, `NormativeProfile`, `DeviationResult`, `AnalysisArtifacts`.

- `src/fra/domain/schemas.py`
  Pydantic-схемы для входных и выходных контрактов.

- `src/fra/domain/enums.py`
  Перечисления категорий стимула, форматов отчета и флагов качества.

### Ввод/вывод

- `src/fra/io/video_reader.py`
  Покадровое чтение видео и формирование `FrameData`.

- `src/fra/io/stimulus_loader.py`
  Преобразование текстового описания стимула в `StimulusDescriptor`.

- `src/fra/io/normative_loader.py`
  Загрузка и валидация нормативного профиля из JSON.

- `src/fra/io/report_writer.py`
  Сохранение итогового отчета и экспорт в JSON/CSV.

### Компьютерное зрение

- `src/fra/vision/face_detector.py`
  Базовый интерфейс обнаружения лица. Сейчас минимальный, оставлен как точка расширения.

- `src/fra/vision/landmark_tracker.py`
  Извлечение landmarks через MediaPipe Face Mesh.

- `src/fra/vision/quality_control.py`
  Оценка пригодности кадра по яркости, резкости и наличию лица.

### Признаки

- `src/fra/features/geometric_features.py`
  Вычисление геометрических признаков из landmarks.

- `src/fra/features/temporal_features.py`
  Обогащение последовательности признаков временной динамикой.

- `src/fra/features/normalizer.py`
  Нормализация относительно baseline-кадра.

### Профилирование реакции

- `src/fra/profiling/reaction_profile_builder.py`
  Построение `ReactionProfile`, оценка onset/peak/recovery.

- `src/fra/profiling/alignment.py`
  Временное выравнивание фактического и нормативного профилей.

### Оценка девиации

- `src/fra/scoring/comparators.py`
  Расчет gap-метрик между фактическим и нормативным профилем.

- `src/fra/scoring/deviation_calculator.py`
  Агрегация gap-метрик в итоговый показатель девиации.

- `src/fra/scoring/confidence.py`
  Оценка надежности результата по качеству трекинга и кадров.

### Отчеты

- `src/fra/reports/json_report.py`
  Сборка полного JSON-отчета с quality-, profile- и deviation-блоками.

- `src/fra/reports/csv_report.py`
  Экспорт временного ряда признаков в CSV.

## Основные классы

- `ReactionAnalysisPipeline`
  Оркестратор всего процесса.

- `VideoReader`
  Источник покадровых данных.

- `FaceLandmarkTracker`
  Преобразует кадр в landmarks лица.

- `FrameQualityAssessor`
  Маркирует качество кадра и пригодность к расчету.

- `GeometricFeatureExtractor`
  Вычисляет мимические признаки по landmarks.

- `FeatureNormalizer`
  Приводит признаки к относительной шкале baseline.

- `ReactionProfileBuilder`
  Формирует временной профиль реакции.

- `ProfileComparator`
  Считает расхождения с нормативным профилем.

- `DeviationCalculator`
  Возвращает итоговый score девиации.

- `ReportWriter`
  Сохраняет итоговые артефакты анализа.

## Поток данных

```text
CLI
  -> ReactionAnalysisPipeline
  -> StimulusDescriptorLoader
  -> VideoReader
  -> FaceLandmarkTracker
  -> FrameQualityAssessor
  -> GeometricFeatureExtractor
  -> TemporalFeatureExtractor
  -> FeatureNormalizer
  -> ReactionProfileBuilder
  -> NormativeProfileLoader
  -> TemporalAligner
  -> ProfileComparator
  -> DeviationCalculator
  -> ConfidenceEstimator
  -> ReportWriter
  -> JSON / CSV
```

## Данные на каждом шаге

1. `VideoReader` выдает список `FrameData`.
2. `FaceLandmarkTracker` дополняет `FrameData.landmarks`.
3. `GeometricFeatureExtractor` строит `FacialFeatureVector`.
4. `ReactionProfileBuilder` агрегирует временной ряд в `ReactionProfile`.
5. `NormativeProfileLoader` создает `NormativeProfile`.
6. `ProfileComparator` формирует словарь компонентных расхождений.
7. `DeviationCalculator` создает `DeviationResult`.
8. `ReactionAnalysisPipeline` упаковывает все в `AnalysisArtifacts`.

## Точки расширения

- заменить эвристику категоризации стимула на внешний классификатор;
- реализовать более точное временное выравнивание;
- добавить конфигурацию признаков и весов scoring через YAML;
- подключить пакетную обработку нескольких видео;
- расширить quality control метриками позы головы и окклюзий.

## Ограничение области применения

Система вычисляет аналитическую метрику отклонения мимической реакции от выбранного нормативного профиля. Она не ставит диагноз, не оценивает психическое состояние и не должна использоваться как медицинский инструмент.
