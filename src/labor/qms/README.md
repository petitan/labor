# QMS JSON Rendszer v2.0

ISO 17025:2018 Minőségirányítási Kézikönyv strukturált JSON reprezentációja **modular architektúrával** és **plugin-based transform rendszerrel**.

## 🎯 Áttekintés

Ez a rendszer a PeTitan Kft. Kalibrálólaboratórium ISO 17025:2018 szabvány szerinti 8 fejezetét konvertálja strukturált JSON formátumba, lehetővé téve a dinamikus QMS dokumentum generálást.

### ✨ Főbb jellemzők

- ✅ **Modular architektúra** - Global + Chapter-specific adatok szeparálva
- ✅ **Plugin-based transforms** - Bővíthető TransformRegistry rendszer
- ✅ **Build-time merge** - Egyetlen `build_qms.py` futtatása generál mindent
- ✅ **Cross-chapter konzisztencia** - Globális adatok (cég, személyzet) egyszer definiálva
- ✅ **Pre-generated assets** - Ábrák (TikZ, draw.io) előre elkészítve, placeholder-ekkel beillesztve
- ✅ **ISO 17025 compliance** - `metadata.iso_mandatory` jelölés minden blokkon

## 📁 Fájlstruktúra

```
qms/
├── global/
│   └── QMS_global_data.json                # Közös adatok (cég, személyzet, szabványok)
│
├── chapters/
│   ├── QMS_ch01_data.json                  # Chapter 1 specifikus adat
│   ├── QMS_ch02_data.json                  # Chapter 2 specifikus adat
│   ... (ch03-ch08)
│
├── templates/
│   ├── QMS_ch01_template.json              # Chapter 1 docjll template
│   ├── QMS_ch02_template.json              # Chapter 2 docjll template
│   ... (ch03-ch08)
│
├── formats/
│   ├── QMS_ch01_format.json                # Chapter 1 mapping config
│   ├── QMS_ch02_format.json                # Chapter 2 mapping config
│   ... (ch03-ch08)
│
├── assets/
│   ├── szervezeti_struktura.pdf            # Chapter 5 - org chart (pre-generated)
│   ├── laboratorium_alaprajz.pdf           # Chapter 6 - lab layout
│   └── ...
│
├── build/
│   ├── QMS_full_input.json                 # Generated: global + all chapters merged
│   ├── QMS_full_template.json              # Generated: all templates merged
│   ├── QMS_full_format.json                # Generated: all formats merged
│   └── QMS_output.json                     # Final: docjll output
│
├── QMS_schema.json                         # Közös docjll output validátor
├── build_qms.py                            # Build script (merge + convert)
└── README.md                               # Ez a fájl
```

## 🔧 Workflow

### 1. Adatok szerkesztése

**Globális adatok** (egy helyen, minden fejezet használja):
```bash
vim qms/global/QMS_global_data.json
```

**Chapter-specifikus adatok**:
```bash
vim qms/chapters/QMS_ch01_data.json
```

### 2. Build futtatása

```bash
cd /home/petitan/labor/src/labor/qms
python3 build_qms.py
```

**Output:**
```
✅ QMS_full_input.json     (global + 8 chapter merged)
✅ QMS_full_template.json  (all templates merged)
✅ QMS_full_format.json    (all mappings merged)
```

### 3. Konverzió build → docjll

```bash
cd /home/petitan/labor/src/labor
python3 qms/convert.py
```

**Output:** `qms/build/QMS_output.json` - Final docjll format

**Converter:** `QMSConverter` plugin (uses Transform Registry for placeholder substitution)

### 4. Konverzió docjll → LaTeX

```python
from docjl import MarkdownJsonToDocjl
import json

# Load generated docjll
with open('qms/build/QMS_output.json') as f:
    docjll_data = json.load(f)

# Convert to LaTeX
converter = MarkdownJsonToDocjl()
latex_output = converter.convert(json.dumps(docjll_data))

# Save
with open('output/qms_manual.tex', 'w') as f:
    f.write(latex_output)
```

### 5. LaTeX → PDF

```bash
cd output
pdflatex qms_manual.tex
pdflatex qms_manual.tex  # Second run for references
```

## 🧩 Transform Registry System

### Regisztrált transformok

```python
from transforms import TransformRegistry

# List all available transforms
TransformRegistry.list_transforms()
# → ['capitalize', 'format_document_list', 'format_regulation_list',
#    'format_standard_list', 'join_with_comma', 'join_with_newline',
#    'join_with_separator', 'lowercase', 'uppercase']
```

### Használat format.json-ban

**Egyszerű transform:**
```json
{
  "mappings": {
    "{{ACTIVITY_LOCATIONS}}": {
      "source": "chapters.ch01.scope.activity_locations",
      "pipeline": [
        {"transform": "join_with_separator", "params": {"separator": " + "}}
      ]
    }
  }
}
```

**Összetett transform chain:**
```json
{
  "mappings": {
    "{{STANDARDS_LIST}}": {
      "source": "global.documents.international_standards",
      "pipeline": [
        {"transform": "format_standard_list"},
        {"transform": "join_with_newline"}
      ]
    }
  }
}
```

### Saját transform hozzáadása

```python
# transforms/custom_transforms.py
from .registry import TransformRegistry

def my_custom_transform(value: str, prefix: str = "") -> str:
    return f"{prefix}{value}"

TransformRegistry.register("my_custom_transform", my_custom_transform)
```

## 📊 Global vs. Chapter-specific adatok

### Global data (`global/QMS_global_data.json`)

**Miért global?** - Több fejezetben is használva, egyszer definiálva:

```json
{
  "company": {
    "name": "PeTitan Informatika Kft.",          // Ch01, Ch05, Ch06, Ch07, Ch08
    "nah_accreditation": "NAH-2-XXXX/20XX"       // Ch01, Ch07
  },
  "personnel": {
    "managing_director": {"name": "Kálmán Péter"},  // Ch05, Ch08
    "quality_manager": {"name": "Szekeres Károly"}  // Ch05, Ch08
  },
  "documents": {
    "international_standards": [...],            // Ch02 (felsorolva)
    "ilac_documents": [...],                     // Ch02, Ch07 (hivatkozva)
    "nar_documents": [...]                       // Ch02, Ch06, Ch07, Ch08
  }
}
```

### Chapter-specific data (`chapters/QMS_ch01_data.json`)

**Miért chapter-specific?** - Csak ebben a fejezetben használva:

```json
{
  "scope": {
    "activity_locations": ["laboratórium", "külső helyszín"],  // Csak Ch01
    "objectives": [...]                                         // Csak Ch01
  }
}
```

## 🖼️ Ábrák kezelése (Pre-generated Assets)

### Ábra előkészítés

**Opció A: TikZ → PDF**
```bash
# Szerkesztés
vim assets/szervezeti_struktura_tikz.tex

# Konverzió
pdflatex szervezeti_struktura_tikz.tex
mv szervezeti_struktura_tikz.pdf assets/szervezeti_struktura.pdf
```

**Opció B: draw.io / Visio / Inkscape**
```
1. Szerkesztés a grafikus szoftverben
2. Export → PDF (vectorgraphic) vagy PNG
3. Mentés → qms/assets/filename.pdf
```

### Ábra beillesztése template-be

**Template** (`templates/QMS_ch05_template.json`):
```json
{
  "type": "figure",
  "image_path": "{{FIG_ORG_CHART_PATH}}",
  "caption": "Laboratórium szervezeti felépítése",
  "label": "fig:szervezeti_struktura",
  "width": "0.8\\textwidth"
}
```

**Chapter data** (`chapters/QMS_ch05_data.json`):
```json
{
  "figures": {
    "org_chart_path": "qms/assets/szervezeti_struktura.pdf"
  }
}
```

**Format mapping** (`formats/QMS_ch05_format.json`):
```json
{
  "mappings": {
    "{{FIG_ORG_CHART_PATH}}": {
      "source": "chapters.ch05.figures.org_chart_path"
    }
  }
}
```

## 📝 tcolorbox Környezetek

### Támogatott box típusok

| Box Style | Jelentés | Szín | Használat |
|-----------|----------|------|-----------|
| `nahinfo` | Információ | Kék | ISO magyarázatok, példák |
| `nahreq` | Követelmény | Zöld | Kötelező előírások |
| `nahalert` | Figyelmeztetés | Piros | Gyakori hibák, veszélyek |
| `nahvalid` | Validáció | Lila | Audithatóság, bizonyítékok |
| `nahsec` | Biztonság | Narancs | Adatvédelem, fizikai biztonság |

### Példa template-ben

```json
{
  "type": "paragraph",
  "metadata": {
    "box_style": "nahinfo",
    "box_title": "[INFO] Alkalmazási terület kulcsadatai"
  },
  "content": "**Alapszabvány:** MSZ EN ISO/IEC 17025:2018\\n**Tevékenység helyszíne:** Laboratórium + külső helyszín"
}
```

## 🧪 Tesztelés

### Build teszt
```bash
cd qms
python3 build_qms.py
# Ellenőrzés:
ls -lh build/
```

### Transform teszt
```bash
cd /home/petitan/labor/src/labor
python3 -c "
from transforms import TransformRegistry
result = TransformRegistry.apply('join_with_separator', ['a', 'b'], {'separator': ' + '})
print(result)  # → 'a + b'
"
```

### JSON Schema validáció
```bash
# TODO: Implement with jsonschema package
pip install jsonschema
python3 validate_qms.py
```

## 📖 Fejezetek státusza

| Chapter | Név | Státusz | Fájlok |
|---------|-----|---------|--------|
| Ch01 | Alkalmazási terület | ✅ Kész | data ✓, template ✓, format ✓ |
| Ch02 | Rendelkező hivatkozások | ✅ Kész | data ✓, template ✓, format ✓ |
| Ch03 | Szakkifejezések | ⏳ Tervezett | - |
| Ch04 | Általános követelmények | ⏳ Tervezett | - |
| Ch05 | Szervezeti követelmények | ⏳ Tervezett | - |
| Ch06 | Erőforrások követelmények | ⏳ Tervezett | - |
| Ch07 | Folyamat követelmények | ⏳ Tervezett | - |
| Ch08 | Irányítási rendszer | ⏳ Tervezett | - |

## 🔗 Kapcsolódó projektek

- **docjl** - JSON to LaTeX konverter (v2.2.3+)
- **calibration_project** - PeTitan QMS LaTeX forrás (legacy)
- **converters/** - Plugin-based converter rendszer
  - `QMSConverter` - QMS dokumentumok konverter
  - `CalibrationConverter` - Kalibrálási eljárások konverter (tervezett)
- **transforms/** - Transform Registry plugin rendszer
- **legacy_converter.py** - Régi generic converter (backward compatibility)

## 🔌 Plugin Architektúra

### Converter Plugins

A rendszer plugin-alapú converter-eket használ minden dokumentum típushoz:

```python
from converters import QMSConverter

converter = QMSConverter()
docjll = converter.convert(
    'qms/build/QMS_full_input.json',
    'qms/build/QMS_full_template.json',
    'qms/build/QMS_full_format.json'
)
```

**Előnyök:**
- ✅ Típus-specifikus konverziós logika
- ✅ Transform Registry integráció
- ✅ Bővíthető új típusokkal
- ✅ Tiszta szeparáció

### Transform Registry

Minden converter a közös Transform Registry-t használja:

```python
from transforms import TransformRegistry

# Elérhető transforms (9 db):
# - join_with_separator, join_with_comma, join_with_newline
# - uppercase, lowercase, capitalize
# - format_standard_list, format_document_list, format_regulation_list
```

## 📜 Verziókezelés

- **v1.0.0** - Chapter 1-2 legacy rendszer (fejezetek izoláltan)
- **v2.0.0** - Modular architektúra + Transform Registry
- **v2.1.0** - Plugin-based converters (jelenlegi)

## 👨‍💻 Licensz

MIT License - PeTitan Informatika Kft. 2025
