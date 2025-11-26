import subprocess
import sys
import os
import time

def run_command(command: list[str]):
    """Segédfüggvény parancsok futtatásához."""
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Hiba történt: {e}\n")
        return e.returncode


def main():
    try:
        print("📦 Python környezet előkészítése...\n")

        # pip frissítése
        print("🔄 pip frissítése...")
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

        # requirements.txt ellenőrzése
        req_path = "requirements.txt"
        if not os.path.isfile(req_path):
            print(f"❌ Nem található a {req_path} fájl!")
            sys.exit(1)

        print("\n📄 requirements.txt betöltése...")
        with open(req_path, "r", encoding="utf-8") as f:
            reqs = [line.strip() for line in f if line.strip()]

        print("\n📦 Telepítendő csomagok:")
        for r in reqs:
            print(f"   - {r}")

        print("\n🚀 Telepítés indul...\n")
        returncode = run_command([sys.executable, "-m", "pip", "install", "-r", req_path])

        if returncode == 0:
            print("\n✅ Minden csomag sikeresen telepítve!")
        else:
            print("\n⚠️ Néhány csomag telepítése sikertelen lehetett.")
    except Exception as e:
        print(f"\n❌ Váratlan hiba történt: {e}\n")
        time.sleep(60)
        sys.exit(1)

if __name__ == "__main__":
    main()
