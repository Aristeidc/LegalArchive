import pytest
from text_normalizer import normalizer


# Exact output: what a stored name looks like after normalizing.
@pytest.mark.parametrize("raw, expected", [
    ("Γεώργιος Παπαδόπουλος", "γεωργιοσ παπαδοπουλοσ"),
    ("ΜΑΡΙΑ ΓΕΩΡΓΙΟΥ", "μαρια γεωργιου"),
    ("Δημήτριος Κωνσταντίνου", "δημητριοσ κωνσταντινου"),
    ("Οδυσσεύς", "οδυσσευσ"),
    # diphthongs
    ("Ευαγγελία Οικονόμου", "ευαγγελια οικονομου"),
    ("ΑΥΓΟΥΣΤΙΝΟΣ ΕΙΡΗΝΑΙΟΥ", "αυγουστινοσ ειρηναιου"),
    # Latin script, Latin accents, casefold vs lower
    ("John Smith", "john smith"),
    ("José Müller", "jose muller"),
    ("Strauß", "strauss"),
    # mixed Greek and English
    ("Παπαδόπουλος Consulting", "παπαδοπουλοσ consulting"),
    # numbers
    ("4Π Συμβουλευτική", "4π συμβουλευτικη"),
    ("Ταβέρνα 1821", "ταβερνα 1821"),
])
def test_names(raw, expected):
    assert normalizer(raw) == expected


# Every combining mark goes: ΐ carries two at once, polytonic carries breathings.
@pytest.mark.parametrize("raw, expected", [
    ("Αϊβαλιώτης", "αιβαλιωτησ"),
    ("ΑΪΒΑΛΙΩΤΗΣ", "αιβαλιωτησ"),
    ("Παΐσιος", "παισιοσ"),
    ("ΠΑΪΣΙΟΣ", "παισιοσ"),
    ("Ἀθανάσιος", "αθανασιοσ"),
])
def test_combining_marks(raw, expected):
    assert normalizer(raw) == expected


# Punctuation becomes a single space.
@pytest.mark.parametrize("raw, expected", [
    ("Ελένη Μάρκου-Βασιλείου", "ελενη μαρκου βασιλειου"),
    ("Ιωάννης-Μάριος Δούκας", "ιωαννησ μαριοσ δουκασ"),
    ("Ελένη Μάρκου\u2013Βασιλείου", "ελενη μαρκου βασιλειου"),  # en dash, as Word inserts it
    ("Παπαδόπουλος - Γεωργίου", "παπαδοπουλοσ γεωργιου"),
    ("Γ. Παπαδόπουλος", "γ παπαδοπουλοσ"),
    ("Αφοί Παπαδόπουλοι Ο.Ε.", "αφοι παπαδοπουλοι ο ε"),
    ("Παπαδόπουλος, Γεώργιος", "παπαδοπουλοσ γεωργιοσ"),
    ("Παπαδόπουλος,Γεώργιος", "παπαδοπουλοσ γεωργιοσ"),
    ("O'Brien", "o brien"),
    ("Νικολάου & ΣΙΑ", "νικολαου σια"),
    ("Πλαστικά Κρήτης 2000 Α.Ε.", "πλαστικα κρητησ 2000 α ε"),
    ("ABC Συμβουλευτική Α.Ε.", "abc συμβουλευτικη α ε"),
])
def test_punctuation(raw, expected):
    assert normalizer(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("Γεώργιος   Παπαδόπουλος", "γεωργιοσ παπαδοπουλοσ"),
    ("Γεώργιος\tΠαπαδόπουλος", "γεωργιοσ παπαδοπουλοσ"),
    ("  Γεώργιος Παπαδόπουλος  ", "γεωργιοσ παπαδοπουλοσ"),
])
def test_whitespace(raw, expected):
    assert normalizer(raw) == expected


# The search guard relies on these coming back empty.
@pytest.mark.parametrize("raw", ["%", "...", "-", "   ", ""])
def test_normalizes_to_empty(raw):
    assert normalizer(raw) == ""


# _ survives, which is why search escapes LIKE wildcards.
@pytest.mark.parametrize("raw, expected", [
    ("_", "_"),
    ("Νίκος_Παπάς", "νικοσ_παπασ"),
])
def test_underscore_survives(raw, expected):
    assert normalizer(raw) == expected


# Pairs that must normalize to the same thing.
@pytest.mark.parametrize("a, b", [
    ("Αριστείδης", "ΑΡΙΣΤΕΙΔΗΣ"),
    ("Αριστείδης", "αριστειδησ"),            # σ typed at the end
    ("Οδυσσεύς", "ΟΔΥΣΣΕΥΣ"),
    ("Αϊβαλιώτης", "Αιβαλιωτης"),            # dialytika left out
    ("Ἀθανάσιος", "Αθανάσιος"),              # polytonic vs monotonic
    ("\u0386", "\u0391\u0301"),              # Ά precomposed vs Α + combining acute
    ("Ελ\u03adνη", "Ελε\u0301νη"),           # έ precomposed vs decomposed
    ("Πα\u0390σιος", "Παι\u0308\u0301σιος"), # ΐ precomposed vs decomposed
])
def test_variants_match(a, b):
    assert normalizer(a) == normalizer(b)