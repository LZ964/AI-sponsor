import zipfile
import os

def create_zip():
    files_to_zip = ['index.html', 'requirements.txt', 'README.md']
    with zipfile.ZipFile('AI-Sponsor-complet.zip', 'w') as zf:
        for f in files_to_zip:
            if os.path.exists(f):
                zf.write(f)
                print(f"Ajouté : {f}")

if __name__ == "__main__":
    create_zip()
