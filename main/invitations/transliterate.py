"""Devanagari → Latin transliteration.

Bihar families write names in Devanagari ("अमन", "प्रिया"), but a readable
shareable URL needs Latin script.  This small converter keeps the URL
meaningful: ``अमन व प्रिया`` becomes ``aman-weds-priya``.
"""

from __future__ import annotations

CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "ऩ": "n", "प": "p", "फ": "ph", "ब": "b", "भ": "bh",
    "म": "m", "य": "y", "र": "r", "ऱ": "r", "ल": "l",
    "ळ": "l", "व": "v", "श": "sh", "ष": "sh", "स": "s",
    "ह": "h", "फ़": "f", "ज़": "z", "ड़": "d", "ढ़": "rh",
}

CONSONANT_CLUSTERS = {
    "क्ष": "ksh", "त्र": "tr", "ज्ञ": "gy", "श्र": "shr",
}

INDEPENDENT_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u",
    "ऊ": "oo", "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o",
    "औ": "au",
}

VOWEL_SIGNS = {
    "ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u",
    "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "ॉ": "o", "ॊ": "e",
}

OTHER_SIGNS = {
    "ं": "n", "ँ": "n", "ः": "h", "ऽ": "", "ॐ": "om",
    "।": "", "॥": "", "॰": "",
}

VIRAMA = "्"

WORD_BOUNDARY = set(" \t\n\r,.;:!?()[]{}|/\\\"'-–—")

NASAL_MARKS = set("ंँ")


def _is_word_boundary(char: str) -> bool:
    """True when the character ends the current word."""

    return char in WORD_BOUNDARY or not ("ऀ" <= char <= "ॿ")


def _is_consonant(char: str) -> bool:
    return char in CONSONANTS or char in CONSONANT_CLUSTERS


def transliterate(text: str) -> str:
    """Return a Latin-script approximation of Devanagari ``text``.

    The rules follow everyday Hindi pronunciation closely enough for URLs:
    a conjunct (explicit virama) keeps no inherent vowel, a word-final
    consonant loses its schwa, and a three-consonant cluster such as
    ``दरभंगा`` renders as ``darbhanga``.
    """

    if not text:
        return ""

    result: list[str] = []
    index = 0
    length = len(text)

    while index < length:
        char = text[index]

        # Legacy clusters written without a virama (क्ष, त्र, ज्ञ, श्र)
        cluster = text[index : index + 2]
        if cluster in CONSONANT_CLUSTERS:
            result.append(CONSONANT_CLUSTERS[cluster])
            index += 2
            continue

        if char in CONSONANTS:
            result.append(CONSONANTS[char])
            index += 1

            if index >= length:
                break

            nxt = text[index]

            if nxt == VIRAMA:
                # Real conjunct: no inherent vowel on this consonant.
                index += 1
                continue

            if nxt in VOWEL_SIGNS:
                result.append(VOWEL_SIGNS[nxt])
                index += 1
                continue

            if nxt in NASAL_MARKS:
                # Anusvara/chandrabindu: the vowel of the consonant stays
                # and the mark is rendered on its own (भं → bhan).
                result.append("a")
                continue

            if _is_word_boundary(nxt):
                # Word-final consonant: the schwa is silent.
                continue

            if _is_consonant(nxt):
                # Three-consonant cluster: the middle vowel disappears.
                if index + 1 < length and _is_consonant(text[index + 1]):
                    continue
                result.append("a")
                continue

            result.append("a")
            continue

        if char in INDEPENDENT_VOWELS:
            result.append(INDEPENDENT_VOWELS[char])
            index += 1
            continue

        if char in VOWEL_SIGNS:
            result.append(VOWEL_SIGNS[char])
            index += 1
            continue

        if char in OTHER_SIGNS:
            result.append(OTHER_SIGNS[char])
            index += 1
            continue

        result.append(char)
        index += 1

    return "".join(result)
