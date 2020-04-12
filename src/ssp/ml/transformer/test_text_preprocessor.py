from ssp.ml.transformer.text_preprocessor import preprocess

def test_preprocess():
    text = '\u2066@rahimzmohamed\u2069 bored already from working at home? Have a little look at my 20 1v1 sessions ebook. ' \
           'Hope it gives you something to try when you can finally return to the training ground! https://t.co/cEClTZnUsP'
    text = preprocess(text=text)
    expected_text = "bore work home have little look 1v1 session ebook hope give try finally return training ground"
    assert text == expected_text