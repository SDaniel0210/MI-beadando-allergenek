import torch
from transformers import pipeline
from typing import Any, Dict, List

# ---- Eszköz kiválasztása (GPU ha van, különben CPU) ----
DEVICE = 0 if torch.cuda.is_available() else -1
print(f"Device set to use {'cuda' if DEVICE == 0 else 'cpu'}")

# ---- Zero-shot nyelvfelismerő pipeline – EGYSZER betöltve ----
LANGUAGES = ["Hungarian", "German", "French", "Spanish", "Italian",
             "Polish", "Romanian", "Russian", "Finnish"]

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=DEVICE
)

# ---- Nyelv -> fordító modell mapping ----
LANG_TO_MODEL = {
    "Hungarian": "Helsinki-NLP/opus-mt-hu-en",
    "German": "Helsinki-NLP/opus-mt-de-en",
    "French": "Helsinki-NLP/opus-mt-fr-en",
    "Spanish": "Helsinki-NLP/opus-mt-es-en",
    "Italian": "Helsinki-NLP/opus-mt-it-en",
    "Polish": "Helsinki-NLP/opus-mt-pl-en",
    "Romanian": "Helsinki-NLP/opus-mt-roa-en",
    "Russian": "Helsinki-NLP/opus-mt-ru-en",
    "Finnish": "Helsinki-NLP/opus-mt-fi-en",
}

# ---- Fordító pipeline-ok cache-ben (ne töltsön le mindig újat) ----
translation_pipelines: Dict[str, Any] = {}


def get_translation_pipeline(model_nev: str):
    """
    Visszaad egy fordító pipeline-t a megadott modellnévhez.
    Cache-eli, hogy ne kelljen minden híváskor újratölteni.
    """
    if model_nev not in translation_pipelines:
        print(f"[DEBUG] Fordító modell betöltése: {model_nev}")
        translation_pipelines[model_nev] = pipeline(
            "translation",
            model=model_nev,
            device=DEVICE
        )
    return translation_pipelines[model_nev]


def split_text_into_chunks(text: str, max_chars: int = 400) -> List[str]:
    """
    Hosszú szöveg feldarabolása max. max_chars hosszú darabokra,
    úgy, hogy lehetőleg szóközöknél törjünk.
    """
    words = text.split()
    chunks: List[str] = []
    current = ""

    for w in words:
        extra_len = len(w) if current == "" else len(w) + 1
        if len(current) + extra_len <= max_chars:
            current = w if current == "" else current + " " + w
        else:
            if current:
                chunks.append(current)
            current = w

    if current:
        chunks.append(current)

    return chunks


def _has_hungarian_accents(text: str) -> bool:
    """Van-e benne tipikus magyar ékezet?"""
    hun_chars = "áéíóöőúüűÁÉÍÓÖŐÚÜŰ"
    return any(ch in text for ch in hun_chars)


def forditas_angolra(szoveg: str) -> str:
    """
    Nyelvfelismerés + fordítás angolra.
    Hosszú szövegeket chunkokra bont, és azokat külön fordítja.
    """
    if not szoveg.strip():
        return ""

    # Nyelvfelismeréshez első ~500 karakter
    minta_szoveg = szoveg[:500]

    result = classifier(
        minta_szoveg,
        LANGUAGES,
        multi_label=False
    )
    labels = result["labels"]
    scores = result["scores"]

    felismert_nyelv = labels[0]
    print("[DEBUG] Nyelvfelismerés eredmény:")
    for lab, sc in zip(labels, scores):
        print(f"    {lab}: {sc:.3f}")

    # ---- Magyar heurisztika ----
    # Ha nem Hungarian-t mond, de vannak magyar ékezetek,
    # és Hungarian is szerepel a listában, akkor force Hungarian.
    if felismert_nyelv != "Hungarian" and _has_hungarian_accents(minta_szoveg):
        if "Hungarian" in labels:
            idx = labels.index("Hungarian")
            # csak akkor erőltetjük, ha nem teljesen random (pl. legalább 0.1 score)
            if scores[idx] >= 0.1:
                print("[DEBUG] Magyar ékezetek + Hungarian a listában -> Override Hungarian-re")
                felismert_nyelv = "Hungarian"

    if felismert_nyelv not in LANG_TO_MODEL:
        print(f"[DEBUG] Ismeretlen nyelv: {felismert_nyelv}, visszaadjuk az eredetit.")
        return szoveg

    model_nev = LANG_TO_MODEL[felismert_nyelv]
    fordito = get_translation_pipeline(model_nev)

    # ---- SZÖVEG DARABOLÁSA ----
    chunks = split_text_into_chunks(szoveg, max_chars=400)
    print(f"[DEBUG] Szöveg {len(chunks)} darabra bontva fordításhoz.")

    translated_chunks: List[str] = []
    for i, ch in enumerate(chunks, start=1):
        eredmeny = fordito(ch, max_length=512)
        translated = eredmeny[0]["translation_text"]
        print(f"[DEBUG] Chunk {i}/{len(chunks)} fordítva. Hossz: {len(translated)}")
        translated_chunks.append(translated)

    angol_szoveg = " ".join(translated_chunks)
    return angol_szoveg


def forditas_magyarra(szoveg: str) -> str:
    """
    Angol → magyar fordítás a felhasználónak szánt végső kimenethez.
    """
    if not szoveg.strip():
        return ""

    model_nev = "Helsinki-NLP/opus-mt-en-hu"
    fordito = get_translation_pipeline(model_nev)

    chunks = split_text_into_chunks(szoveg, max_chars=400)
    print(f"[DEBUG] (en→hu) Szöveg {len(chunks)} darabra bontva.")

    translated_chunks: List[str] = []
    for i, ch in enumerate(chunks, start=1):
        eredmeny = fordito(ch, max_length=512)
        translated = eredmeny[0]["translation_text"]
        print(f"[DEBUG] (en→hu) Chunk {i}/{len(chunks)} fordítva. Hossz: {len(translated)}")
        translated_chunks.append(translated)

    magyar_szoveg = " ".join(translated_chunks)
    return magyar_szoveg
