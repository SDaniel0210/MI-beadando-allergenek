import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QTextEdit, QFrame, QFileDialog,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PIL import Image
import easyocr
import numpy as np
from allergen_felismero import forditas_angolra, forditas_magyarra
from TextAllergenDetector import TextAllergenDetector


# ==== EASYOCR OLVASÓ BETÖLTÉSE ====
# több nyelv akkor: ['en', 'hu']
reader = easyocr.Reader(['en','hu'], gpu=False)

def run_ocr_on_file(file_path: str) -> str:
    """
    EasyOCR-alapú OCR.
    Bemenet: képfájl útvonal
    Kimenet: felismert szöveg (string)
    Itt PIL-lal olvassuk be a képet, hogy ne haljon meg az ékezetes útvonaltól.
    """
    # 1) Kép beolvasása PIL-lel
    image = Image.open(file_path).convert("RGB")

    # 2) PIL -> numpy tömb
    img_np = np.array(image)

    # 3) EasyOCR-t már a numpy tömbbel hívjuk, nem path-tal
    results = reader.readtext(img_np, detail=0)  # detail=0 -> csak a szöveg

    text = "\n".join(results)
    return text.strip()

#fordító modell bekötése:
def translate_text(text: str) -> str:

    if not text.strip():
        return ""

    # Ha itt hiba van, hadd kapja el a GUI (handle_translate)
    angol_szoveg = forditas_angolra(text)
    return angol_szoveg


detector = TextAllergenDetector()

#allergén modell bekötése:
def extract_allergens(text: str):
    """
    Allergének kinyerése Krisz keyword-detektorával (angol szöveg).
    Visszatér: lista dict-ekkel.
    """
    if not text.strip():
        return []

    return detector.detect(text)


# ====== Teljes UI======
# ====== DRAG & DROP ZÓNA ======

class FileDropArea(QFrame):
    """
    Egy saját drop zóna, ami fájlokat fogad, és jelzi a főablaknak,
    ha kapott egy fájlt.
    """

    def mousePressEvent(self, event):
        """
        Ha a felhasználó rákattint a zónára, fájlválasztó ablakot hozunk fel.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Fájl kiválasztása",
            "",
            "Képfájlok (*.png *.jpg *.jpeg *.bmp *.gif);;Minden fájl (*.*)"
        )

        if file_path:
            file_name = os.path.basename(file_path)
            self.set_text(f"Fájl kiválasztva:\n{file_name}")
            self.file_dropped.emit(file_path)


    file_dropped = Signal(str)  # a kiválasztott fájl elérési útja
    def __init__(self, text: str = ""):
        super().__init__()

        self.setAcceptDrops(True)

        self._normal_style = """
            QFrame {
                border: 2px dashed #000000;
                border-radius: 12px;
                background-color: #2077d4;
            }
        """
        self._highlight_style = """
            QFrame {
                border: 2px solid #ffffff;
                border-radius: 12px;
                background-color: #e8f5e9;
            }
        """

        self.setStyleSheet(self._normal_style)
        self.setMinimumHeight(200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #ffffff; font-size: 14px;")

        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_text(self, text: str):
        self.label.setText(text)

    # ---- Drag & drop eventek ----

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self._highlight_style)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._normal_style)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return

        file_path = urls[0].toLocalFile()

        self.setStyleSheet(self._normal_style)

        file_name = os.path.basename(file_path)
        self.set_text(f"Fájl kiválasztva:\n{file_name}")

        self.file_dropped.emit(file_path)


# ====== FŐABLAK ======

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ablak alap
        self.setWindowTitle("Allergének Felismerő")
        self.resize(1000, 750)

        # Belső állapotok
        self.current_file_path: str | None = None
        self.ocr_text: str | None = None
        self.translated_text: str | None = None

        # -------- 1) Központi widget + fő layout --------
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # -------- 2) Fejléc --------
        title_label = QLabel("OCR + Nyelvfelismerés + Allergének")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        subtitle_label = QLabel(
            "1) Húzd ide a képet / fájlt\n"
            "2) OCR futtatása\n"
            "3) Fordítás\n"
            "4) Allergének listázása"
        )
        subtitle_label.setAlignment(Qt.AlignLeft)
        subtitle_label.setStyleSheet("color: gray; font-size: 12px;")

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        # -------- 3) Drag & Drop zóna --------
        self.drop_area = FileDropArea(
            "Húzd ide a fájlt (kép / PDF)\n"
            "vagy kattints a megnyitáshoz (később)"
        )
        self.drop_area.file_dropped.connect(self.on_file_dropped)

        main_layout.addWidget(self.drop_area)

        # -------- 4) Gombok sor --------
        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        self.ocr_button = QPushButton("OCR futtatása")
        self.translate_button = QPushButton("Fordítás")
        self.allergen_button = QPushButton("Allergének")
        self.clear_button = QPushButton("Törlés")

        button_row.addWidget(self.ocr_button)
        button_row.addWidget(self.translate_button)
        button_row.addWidget(self.allergen_button)
        button_row.addWidget(self.clear_button)
        button_row.addStretch()

        main_layout.addLayout(button_row)

        # -------- 5) Státusz / log mező --------
        status_label = QLabel("Folyamatlog:")
        status_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(status_label)

        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setPlaceholderText(
            "Itt fog megjelenni, hogy az OCR / Fordítás / Allergének lépések "
            "sikeresen lefutottak-e, vagy ha hiba történt."
        )
        self.status_log.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        self.status_log.setMaximumHeight(120)

        main_layout.addWidget(self.status_log)

        # -------- 6) Allergének eredmény mező --------
        result_label = QLabel("Allergének listája:")
        result_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Itt fog megjelenni az allergének listája.")
        self.result_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
            }
        """)

        main_layout.addWidget(self.result_text)

        # ---- Gombok eseményei ----
        self.clear_button.clicked.connect(self.clear_all)
        self.ocr_button.clicked.connect(self.handle_ocr)
        self.translate_button.clicked.connect(self.handle_translate)
        self.allergen_button.clicked.connect(self.handle_allergens)

    # ====== Segédfüggvények ======

    def append_status(self, message: str, level: str = "info"):
        """
        Log bejegyzés a státusz mezőbe.
        level: "info", "success", "error"
        """
        colors = {
            "info": "#ffffff",
            "success": "#a5d6a7",
            "error": "#ef9a9a"
        }
        prefixes = {
            "info": "[INFO]",
            "success": "[OK]",
            "error": "[HIBA]"
        }
        color = colors.get(level, "#ffffff")
        prefix = prefixes.get(level, "[INFO]")

        self.status_log.append(
            f'<span style="color:{color}">{prefix} {message}</span>'
        )

    # ====== Eseménykezelők ======

    def on_file_dropped(self, file_path: str):
        self.current_file_path = file_path
        self.append_status(f"Fájl kiválasztva: {file_path}", "info")

    def clear_all(self):
        self.current_file_path = None
        self.ocr_text = None
        self.translated_text = None

        self.drop_area.set_text(
            "Húzd ide a fájlt (kép / PDF)\n"
            "vagy kattints a megnyitáshoz (később)"
        )
        self.status_log.clear()
        self.result_text.clear()
        self.append_status("Minden mező törölve.", "info")

    def handle_ocr(self):
        if not self.current_file_path:
            self.append_status("OCR futtatása sikertelen: nincs kiválasztott fájl.", "error")
            return

        try:
            self.ocr_text = run_ocr_on_file(self.current_file_path)
            self.append_status("OCR sikeresen lefutott.", "success")
            self.append_status(f"OCR eredmény első 200 karakter: {self.ocr_text[:200]}", "info")

        except Exception as e:
            self.append_status(f"OCR hiba: {e}", "error")

    def handle_translate(self):
        if not self.ocr_text:
            self.append_status("Fordítás sikertelen: nincs OCR szöveg.", "error")
            return

        self.append_status("Fordítás folyamatban, modellek betöltése...", "info")

        try:
            self.translated_text = translate_text(self.ocr_text)
            if not self.translated_text:
                self.append_status("Fordítás nem adott eredményt.", "error")
                return

            self.append_status("Fordítás sikeresen lefutott.", "success")
            self.append_status(
                f"Fordítás (angol) első 200 karakter: {self.translated_text[:200]}",
                "info"
            )
        except Exception as e:
            self.append_status(f"Fordítás hiba: {e}", "error")
            self.translated_text = None

    def handle_allergens(self):
        if not self.translated_text and not self.ocr_text:
            self.append_status("Allergének keresése sikertelen: nincs szöveg.", "error")
            return

        source_text = self.translated_text or self.ocr_text or ""

        try:
            allergens = extract_allergens(source_text)

            self.result_text.clear()
            if allergens:
                self.result_text.append("Talált allergének:\n")
                for a in allergens:
                    self.result_text.append(f"Allergén: {forditas_magyarra(a['name'])}")
                    self.result_text.append(f"Kategória: {forditas_magyarra(a['category'])}")
                    self.result_text.append(f"Leírás: {forditas_magyarra(a['description'])}")
                    self.result_text.append("")  # üres sor
                self.append_status("Allergének sikeresen listázva.", "success")
            else:
                self.result_text.append("Nem találtunk allergéneket.")
                self.append_status("Allergének keresése lefutott, de nem talált semmit.", "info")

        except Exception as e:
            self.append_status(f"Allergén keresés hiba: {e}", "error")


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
