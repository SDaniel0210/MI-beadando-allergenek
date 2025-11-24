import re
from typing import Dict, List, Any, Optional

# ---------- 14 MAJOR EU/UK ALLERGENS ----------
ALLERGEN_KEYWORDS: Dict[str, Dict[str, Any]] = {
    "gluten": {
        "name": "Cereals containing gluten",
        "category": "Cereal protein",
        "description": (
            "Gluten is found in wheat, barley, rye, and related grains. "
            "It can trigger symptoms in people with celiac disease or non-celiac gluten sensitivity."
        ),
        "keywords": [
            "gluten", "wheat", "barley", "rye", "spelt", "durum", "semolina",
            "bulgur", "couscous", "farro", "triticale", "malt", "brewer's yeast",
            "flour", "breadcrumbs", "pasta", "noodles", "bread", "cracker", "biscuit", "cake"
        ],
    },
    "crustaceans": {
        "name": "Crustaceans",
        "category": "Shellfish allergy (crustaceans)",
        "description": (
            "Crustacean allergy includes shrimp, crab, lobster, and similar seafood. "
            "Reactions can be severe and cooking vapors may also trigger symptoms."
        ),
        "keywords": [
            "crustacean", "shrimp", "prawn", "prawns", "crab", "lobster",
            "crayfish", "langoustine", "scampi"
        ],
    },
    "molluscs": {
        "name": "Molluscs",
        "category": "Shellfish allergy (molluscs)",
        "description": (
            "Mollusc allergy includes mussels, oysters, clams, squid, and octopus. "
            "Often lifelong and can cause serious reactions."
        ),
        "keywords": [
            "mollusc", "mollusk", "mussels", "oyster", "oysters", "clam", "clams",
            "scallop", "scallops", "octopus", "squid", "calamari", "snail", "escargot"
        ],
    },
    "egg": {
        "name": "Egg",
        "category": "Animal protein allergy",
        "description": (
            "Egg allergy is a reaction to proteins in egg white or yolk. "
            "Common in children; can cause skin, digestive, or respiratory symptoms."
        ),
        "keywords": [
            "egg", "eggs", "egg white", "egg yolk", "omelette", "mayonnaise", "mayo",
            "meringue", "custard", "albumin", "aioli"
        ],
    },
    "fish": {
        "name": "Fish",
        "category": "Animal protein allergy",
        "description": (
            "Fish allergy is an immune response to fish proteins (e.g., salmon, tuna). "
            "It can be severe; even fumes from cooking may provoke reactions."
        ),
        "keywords": [
            "fish", "salmon", "tuna", "cod", "trout", "haddock", "mackerel",
            "sardine", "anchovy", "herring", "pollock", "tilapia"
        ],
    },
    "peanut": {
        "name": "Peanut",
        "category": "Legume allergy",
        "description": (
            "Peanut allergy is one of the most common severe food allergies. "
            "Tiny amounts can cause reactions up to anaphylaxis."
        ),
        "keywords": [
            "peanut", "peanuts", "peanut butter", "groundnut", "satay"
        ],
    },
    "soy": {
        "name": "Soybean",
        "category": "Legume allergy",
        "description": (
            "Soy allergy involves reactions to soybeans or soy products. "
            "Common in infants and children, sometimes improves with age."
        ),
        "keywords": [
            "soy", "soya", "soybean", "tofu", "soy sauce", "tamari",
            "edamame", "miso", "tempeh", "natto"
        ],
    },
    "milk": {
        "name": "Milk",
        "category": "Dairy allergy",
        "description": (
            "Milk allergy is an immune reaction to milk proteins (casein/whey). "
            "Different from lactose intolerance; can cause hives, vomiting, or anaphylaxis."
        ),
        "keywords": [
            "milk", "cheese", "butter", "cream", "yogurt", "lactose",
            "whey", "casein", "curd", "ghee", "ice cream", "cream cheese",
            "cheddar", "mozzarella", "parmesan", "gouda"
        ],
    },
    "tree_nuts": {
        "name": "Tree nuts",
        "category": "Nut allergy",
        "description": (
            "Tree nut allergy includes almonds, hazelnuts, walnuts, cashews, pistachios, etc. "
            "Often lifelong and can be severe."
        ),
        "keywords": [
            "tree nut", "tree nuts", "almond", "almonds", "hazelnut", "hazelnuts",
            "walnut", "walnuts", "cashew", "cashews", "pistachio", "pistachios",
            "pecan", "pecans", "brazil nut", "brazil nuts", "macadamia",
            "queensland nut"
        ],
    },
    "celery": {
        "name": "Celery",
        "category": "Vegetable allergy",
        "description": (
            "Celery allergy can cause reactions from mild oral itching to severe symptoms. "
            "Celery may appear in soups, spice mixes, and processed foods."
        ),
        "keywords": [
            "celery", "celeriac", "celery root", "celery salt", "celery seed"
        ],
    },
    "mustard": {
        "name": "Mustard",
        "category": "Seed/spice allergy",
        "description": (
            "Mustard allergy can be strong and sometimes cross-reacts with other seeds. "
            "Mustard may hide in sauces, dressings, and spice blends."
        ),
        "keywords": [
            "mustard", "mustard seed", "mustard seeds", "dijon",
            "yellow mustard", "wholegrain mustard", "mustard powder"
        ],
    },
    "sesame": {
        "name": "Sesame",
        "category": "Seed allergy",
        "description": (
            "Sesame allergy is increasingly common and can be severe. "
            "Typical triggers include sesame seeds, oil, and tahini."
        ),
        "keywords": [
            "sesame", "sesame seed", "sesame seeds", "tahini", "sesame oil"
        ],
    },
    "sulphites": {
        "name": "Sulphur dioxide / Sulphites",
        "category": "Preservative sensitivity",
        "description": (
            "Sulphites (preservatives) can trigger asthma-like symptoms or hives in sensitive individuals. "
            "Common in wine, dried fruit, and some processed foods."
        ),
        "keywords": [
            "sulphite", "sulphites", "sulfite", "sulfites",
            "sulphur dioxide", "sulfur dioxide",
            "e220", "e221", "e222", "e223", "e224", "e225", "e226", "e227", "e228"
        ],
    },
    "lupin": {
        "name": "Lupin",
        "category": "Legume allergy",
        "description": (
            "Lupin is a legume often used as flour in gluten-free products. "
            "People with peanut allergy may cross-react to lupin."
        ),
        "keywords": [
            "lupin", "lupine", "lupin flour", "lupin bean"
        ],
    },
}

# ---------- TEXT-BASED ALLERGEN DETECTOR CLASS ----------
class TextAllergenDetector:
    """
    Detects allergens in an English text using keyword matching.

    Input:  English text (str)
    Output: List[dict] with detected allergens and their descriptions.
    """

    def __init__(self, allergen_data: Optional[Dict[str, Dict[str, Any]]] = None):
        self.allergen_data = allergen_data or ALLERGEN_KEYWORDS
        self._patterns = self._compile_patterns(self.allergen_data)

    @staticmethod
    def _normalize(text: str) -> str:
        return (
            text.lower()
                .replace("’", "'")
                .replace("–", "-")
                .replace("—", "-")
        )

    @staticmethod
    def _compile_patterns(allergen_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[re.Pattern]]:
        patterns: Dict[str, List[re.Pattern]] = {}
        for allergen_id, data in allergen_data.items():
            pats = []
            for kw in data.get("keywords", []):
                kw_norm = kw.lower()
                kw_esc = re.escape(kw_norm)

                if " " in kw_norm:
                    parts = [re.escape(p) for p in kw_norm.split()]
                    phrase = r"\b" + r"[\s\-]+".join(parts) + r"\b"
                    pats.append(re.compile(phrase))
                else:
                    pats.append(re.compile(rf"\b{kw_esc}\b"))

            patterns[allergen_id] = pats
        return patterns

    def detect(self, text: str) -> List[Dict[str, Any]]:
        norm = self._normalize(text)
        results: List[Dict[str, Any]] = []

        for allergen_id, pats in self._patterns.items():
            matched = False
            for pat in pats:
                if pat.search(norm):
                    matched = True
                    break

            if matched:
                data = self.allergen_data[allergen_id]
                results.append({
                    "id": allergen_id,
                    "name": data["name"],
                    "category": data["category"],
                    "description": data["description"],
                })

        return results


# ---------- EXAMPLE ----------
"""
if __name__ == "__main__":
    detector = TextAllergenDetector()

    text = "A creamy pasta with parmesan and sesame topping, served with garlic bread."
    found = detector.detect(text)

    if not found:
        print("No allergens detected.")
    else:
        print("Detected allergens:")
        for item in found:
            print(f"\n--- {item['name']} ---")
            print(f"Category: {item['category']}")
            print(f"Info: {item['description']}")
"""