# facial-reaction-analysis

Python-проект для модуля компьютерного зрения, который принимает видео мимической реакции человека и описание визуального стимула, извлекает мимические признаки, строит временной профиль реакции, сравнивает его с нормативным профилем и рассчитывает показатель девиации.

Проект решает аналитическую задачу и не предназначен для медицинской диагностики.

## Требования

- Python 3.10+
- `opencv-python`
- `mediapipe`
- `numpy`
- `pandas`
- `pydantic`

## Быстрый старт

```bash
pip install -e .
fra analyze --video path/to/reaction.mp4 --stimulus "pleasant surprise image" --norm data/normative_profiles/default_profile.json --out data/reports/report.json --out-csv data/reports/timeline.csv
```

## CLI

```bash
fra analyze --video VIDEO --stimulus TEXT --norm PROFILE.json --out REPORT.json [--out-csv TIMELINE.csv]
fra analyze-dataset-video --video VIDEO --dataset oasis|gaped|artemis [--stimulus-id ID] --out REPORT.json [--out-csv TIMELINE.csv] [--save-generated-norm NORM.json]
fra run-session --dataset oasis|gaped|artemis [--stimulus-id ID] [--category CATEGORY] --out REPORT.json [--out-csv TIMELINE.csv] [--save-generated-norm NORM.json]
fra run-study --dataset oasis|gaped|artemis --count N --out STUDY.json [--out-csv STUDY.csv] [--artifacts-dir DIR]
fra list-stimuli --dataset oasis|gaped|artemis [--category CATEGORY] [--limit 20]
fra validate-profile --norm PROFILE.json
fra export-report --input REPORT.json --format json|csv --out OUTPUT
```

## Работа со стимулами из датасетов

Для практического сценария в проекте используются локальные наборы стимулов:

- `OASIS`: изображения и нормативные оценки `valence/arousal`;
- `GAPED`: изображения и нормативные оценки `valence/arousal` с SD.
- `ArtEmis` + `wiki_art`: изображения произведений искусства, распределения эмоций зрителей и текстовые объяснения ожидаемой реакции.

Для интерпретации наблюдаемой мимической реакции используется label space из `FER/CK+`:

- `angry`
- `disgust`
- `fear`
- `happy`
- `neutral`
- `sad`
- `surprise`

Команда `run-session`:

1. выбирает изображение из `OASIS` или `GAPED`;
2. показывает его на экране через OpenCV;
3. записывает реакцию пользователя с веб-камеры;
4. строит нормативный профиль реакции на основе нормативных оценок стимула;
5. рассчитывает отклонение фактической мимической реакции от этой нормы;
6. сохраняет JSON/CSV-отчет.

Пример:

```bash
fra run-session --dataset oasis --stimulus-id I1 --out data/reports/session_report.json --out-csv data/reports/session_timeline.csv
```

Если видео реакции уже записано отдельно, можно использовать:

```bash
fra analyze-dataset-video --video data/samples/reaction.mp4 --dataset oasis --stimulus-id I1 --out data/reports/report.json --out-csv data/reports/timeline.csv --save-generated-norm data/reports/generated_norm.json
```

Для просмотра доступных стимулов:

```bash
fra list-stimuli --dataset gaped --category positive --limit 10
fra list-stimuli --dataset artemis --category positive --limit 10
```

Для полноценной серии стимулов с камерой и итоговым отчетом:

```bash
fra run-study --dataset artemis --count 5 --out data/reports/study_report.json --out-csv data/reports/study_report.csv --artifacts-dir data/reports/study_artifacts
```

## Структура проекта

```text
src/fra/
  api/         orchestration pipeline
  cli.py       CLI-конфигурация и аргументы
  domain/      доменные модели и Pydantic-схемы
  features/    геометрические и временные признаки
  io/          чтение видео, загрузка профилей, запись отчетов
  profiling/   построение и выравнивание временного профиля реакции
  reports/     сборка JSON/CSV-представлений
  scoring/     сравнение с нормативом и расчет девиации
  vision/      трекинг landmarks и контроль качества кадров
docs/
  architecture.md   архитектурная схема и поток данных
  data_contracts.md контракты доменных сущностей
tests/
  тесты CLI, профиля, scoring, reports
```

Подробности по назначению файлов и основных классах вынесены в [docs/architecture.md](docs/architecture.md) и [docs/data_contracts.md](docs/data_contracts.md).

## Поток данных

1. CLI получает путь к видео, описание стимула и нормативный профиль.
2. `VideoReader` читает видео покадрово.
3. `FaceLandmarkTracker` извлекает facial landmarks через MediaPipe Face Mesh.
4. `FrameQualityAssessor` оценивает пригодность кадра.
5. `GeometricFeatureExtractor` и `TemporalFeatureExtractor` формируют последовательность мимических признаков.
6. `FeatureNormalizer` нормализует признаки относительно базового кадра.
7. `ReactionProfileBuilder` строит временной профиль реакции.
8. `TemporalAligner` и `ProfileComparator` сопоставляют профиль с нормативным.
9. `DeviationCalculator` и `ConfidenceEstimator` считают итоговую метрику девиации и доверие к оценке.
10. `ReportWriter` сохраняет JSON- и CSV-отчеты.

## Как строится норма

В текущей версии норма строится не из датасета видеореакций лица, а из семантики и нормативных характеристик самого стимула:

1. для выбранного изображения берутся `valence_mean`, `arousal_mean` и, если доступны, `SD`;
2. для `ArtEmis` дополнительно агрегируются эмоции зрителей и их текстовые объяснения (`utterance`);
3. по `ArtEmis`-эмоциям строится mapping в наблюдаемые facial emotion classes (`FER/CK+` label space);
4. по `valence` определяется полярность стимула: `positive`, `neutral`, `negative`;
5. по `arousal` определяется ожидаемая интенсивность и скорость реакции;
6. генератор строит шаблонный временной профиль `baseline -> onset -> peak -> recovery`;
7. tolerances для amplitude/latency/symmetry/recovery масштабируются с учетом вариативности оценок стимула.

Это аналитическая эвристическая норма, основанная на метаданных стимулов, а не популяционная клиническая норма.

## Как интерпретируется реакция

1. Из `ArtEmis` или из категории стимула определяется ожидаемый набор реакций.
2. Он переводится в наблюдаемые facial emotion classes: например `awe -> surprise/happy`, `sadness -> sad/neutral`, `fear -> fear/surprise`.
3. По peak-мимическим признакам фактической реакции выбирается ближайший наблюдаемый класс.
4. В отчет добавляется интерпретация:
   - какие реакции ожидались;
   - какая реакция наблюдалась;
   - совпадает ли она с ожидаемым набором;
   - каков вклад amplitude/latency/symmetry/recovery в общее отклонение.

## Ограничения

- Предполагается один человек в кадре.
- Качество оценки зависит от освещения, ракурса, окклюзий и стабильности трекинга.
- Для `run-session` нужна доступная веб-камера и рабочий GUI для окон OpenCV.
- Для `run-study` также нужна доступная веб-камера; по каждому стимулу будет записан отдельный видеофайл реакции.
- В репозитории нет полноценного датасета пар `стимул -> видео мимической реакции лица`, поэтому норма реакции строится эвристически по параметрам стимула.
- Результат не должен интерпретироваться как медицинское заключение.
