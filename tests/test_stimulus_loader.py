from fra.io.stimulus_loader import StimulusDescriptorLoader


def test_stimulus_loader_infers_positive_category() -> None:
    loader = StimulusDescriptorLoader()
    descriptor = loader.load("pleasant surprise image")
    assert descriptor.category == "positive"
    assert descriptor.stimulus_id == "pleasant_surprise_image"
