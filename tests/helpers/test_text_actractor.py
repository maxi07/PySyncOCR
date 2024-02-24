from src.helpers.OpenAI import extract_text


def test_text_extractor():
    res = extract_text("tests/assets/midi_withtext.pdf")
    assert "The  LinnSequencer  is a state-of-the-art  composition  and  performance  tool  for the professional  musician." in res
