import torch
from transformers import pipeline

# függvény a beolvasott szöveg angolra fordításához, a következő lépéshez
def forditas_angolra(szoveg):
    classifier = pipeline(
        "zero-shot-classification", 
        model="facebook/bart-large-mnli",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    nyelvek = ["Hungarian", "German", "French", "Spanish", "Italian", "Polish","Romanian","Russian","Finnish"]

    result = classifier(
        szoveg, 
        nyelvek, 
        multi_label=False
    )
    felismert_nyelv = result['labels'][0]

    if felismert_nyelv == "Hungarian":
        model_nev = "Helsinki-NLP/opus-mt-hu-en"
    elif felismert_nyelv == "German":
        model_nev = "Helsinki-NLP/opus-mt-de-en"
    elif felismert_nyelv == "French":
        model_nev = "Helsinki-NLP/opus-mt-fr-en"
    elif felismert_nyelv == "Spanish":
        model_nev = "Helsinki-NLP/opus-mt-es-en"
    elif felismert_nyelv == "Italian":
        model_nev = "Helsinki-NLP/opus-mt-it-en"
    elif felismert_nyelv == "Polish":
        model_nev = "Helsinki-NLP/opus-mt-pl-en"
    elif felismert_nyelv == "Romanian":
        model_nev = "Helsinki-NLP/opus-mt-roa-en"
    elif felismert_nyelv == "Russian":
        model_nev = "Helsinki-NLP/opus-mt-ru-en"
    elif felismert_nyelv == "Finnish":
        model_nev = "Helsinki-NLP/opus-mt-fi-en"
    else:
        return szoveg

    fordito=pipeline("translation", model=model_nev)
    eredmeny= fordito(szoveg)
    angol_szoveg=eredmeny[0]['translation_text']

    return angol_szoveg

# angolra_forditott=input("Adj meg egy szöveget valamilyen nyelven: ")
# angolra_forditott= forditas_angolra(angolra_forditott) if angolra_forditott!="" else ""
# print(angolra_forditott)

#függvény a felismert allergének magyarra fordításához a felhasználó számára
def forditas_magyarra(szoveg):
    fordito=pipeline("translation", model="Helsinki-NLP/opus-mt-en-hu")
    eredmeny= fordito(szoveg)
    magyar_szoveg=eredmeny[0]['translation_text']
    return magyar_szoveg

# magyarra_forditott= forditas_magyarra(angolra_forditott) if angolra_forditott!="" else ""
# print(magyarra_forditott)