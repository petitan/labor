# Transforms Package

Transform Registry és újrafelhasználható formázási helper-ek a docjl inline array-ekhez.

## Áttekintés

A `transforms` csomag két fő funkciót lát el:

1. **Transform Registry** - Plugin-alapú adat transzformációs rendszer
2. **Formatting Helpers** - Újrafelhasználható helper-ek docjl inline array generáláshoz

## Transform Registry

### Használat

```python
from transforms import TransformRegistry

# Elérhető transform-ok listája
transforms = TransformRegistry.list_transforms()
# → ['capitalize', 'format_document_list', 'join_with_separator', ...]

# Transform alkalmazása
result = TransformRegistry.apply('join_with_separator', ['a', 'b', 'c'], {'separator': ' + '})
# → 'a + b + c'
```

### Regisztrált Transform-ok

#### Általános Transform-ok (`common_transforms.py`)

- `join_with_separator(items, params={'separator': ', '})` - Lista elemek összefűzése egyedi elválasztóval
- `join_with_comma(items)` - Lista elemek összefűzése vesszővel
- `join_with_newline(items)` - Lista elemek összefűzése sortöréssel
- `uppercase(text)` - Nagybetűssé alakítás
- `lowercase(text)` - Kisbetűssé alakítás
- `capitalize(text)` - Első betű nagybetű

#### QMS Transform-ok (`qms_transforms.py`)

- `format_standard_list(items)` - ISO szabványok félkövér formázással
- `format_document_list(items)` - ILAC/NAR dokumentumok félkövér formázással
- `format_regulation_list(items)` - Magyar rendeletek félkövér formázással

### Saját Transform Regisztrálása

```python
from transforms import TransformRegistry

def my_transform(value, params=None):
    # Transform logika
    return processed_value

TransformRegistry.register('my_transform', my_transform)
```

## Formatting Helpers

Az újrafelhasználható helper függvények docjl inline array-ek generálásához.

### Miért vannak?

A docjl inline array-ek (`[{"type": "bold", "content": "..."}]`) a docjl natív formátuma a formázott szöveghez. A helper-ek DRY principle szerint központosítják ezt a logikát.

### Elérhető Helper-ek

#### 1. `make_bold_prefix(prefix, text, separator=" -- ")`

Félkövér prefix + sima szöveg (dokumentum kódok, szabványok).

```python
from transforms import make_bold_prefix

result = make_bold_prefix("NAR-87", "Pártatlansági Tanácsadó Testület ügyrendje*")
# → [{'type': 'bold', 'content': 'NAR-87'},
#    {'type': 'text', 'content': ' -- Pártatlansági Tanácsadó Testület ügyrendje*'}]
```

**Használati esetek:**
- Dokumentum kódok (NAR-87, ILAC-P8)
- Szabványok (ISO 17025:2018)
- Rendeletek (1/1990 KHVM)

#### 2. `make_bold_label_value(label, value, separator=":")`

Félkövér címke + sima érték (címke-érték párok).

```python
from transforms import make_bold_label_value

result = make_bold_label_value("Alapszabvány", "ISO 17025:2018")
# → [{'type': 'bold', 'content': 'Alapszabvány:'},
#    {'type': 'text', 'content': ' ISO 17025:2018'}]
```

**Használati esetek:**
- Info box tartalmak
- Metaadat megjelenítés
- Specifikációs listák

#### 3. `make_info_box_content(fields)`

Info box tartalom generálás címke-érték párokból.

```python
from transforms import make_info_box_content

fields = {
    'Alapszabvány': 'ISO 17025:2018',
    'Cél': 'Akkreditáció',
    'Terület': 'Kalibrálás'
}

result = make_info_box_content(fields)
# → [{'type': 'bold', 'content': 'Alapszabvány:'},
#    {'type': 'text', 'content': ' ISO 17025:2018\n\n'},
#    {'type': 'bold', 'content': 'Cél:'},
#    {'type': 'text', 'content': ' Akkreditáció\n\n'},
#    {'type': 'bold', 'content': 'Terület:'},
#    {'type': 'text', 'content': ' Kalibrálás'}]
```

**Megjegyzés**: Az utolsó érték után NINCS `\n\n` hogy ne legyen felesleges hely az info box végén.

#### 4. `make_bold_text(text)`, `make_italic_text(text)`, `make_plain_text(text)`

Egyszerű formázott elem létrehozás.

```python
from transforms import make_bold_text, make_italic_text

bold = make_bold_text("Fontos")
# → [{'type': 'bold', 'content': 'Fontos'}]

italic = make_italic_text("Megjegyzés")
# → [{'type': 'italic', 'content': 'Megjegyzés'}]
```

#### 5. `combine_inline_arrays(*arrays)`

Több inline array összefűzése.

```python
from transforms import make_bold_text, make_italic_text, combine_inline_arrays

result = combine_inline_arrays(
    make_bold_text("Bold"),
    [{"type": "text", "content": " és "}],
    make_italic_text("Italic")
)
# → [{'type': 'bold', 'content': 'Bold'},
#    {'type': 'text', 'content': ' és '},
#    {'type': 'italic', 'content': 'Italic'}]
```

## Példa: QMS Transform Refaktorálás

### Előtte (kézzel írt inline array-ek)

```python
def format_standard_list(items: list[dict]) -> list[list[dict]]:
    result = []
    for item in items:
        inline_array = [
            {"type": "bold", "content": item['code']},
            {"type": "text", "content": f" -- {item['title_hun']}*"}
        ]
        result.append(inline_array)
    return result
```

### Utána (helper használattal)

```python
from .formatting_helpers import make_bold_prefix

def format_standard_list(items: list[dict]) -> list[list[dict]]:
    return [
        make_bold_prefix(item['code'], f"{item['title_hun']}*", " -- ")
        for item in items
    ]
```

**Előnyök:**
- ✅ Rövidebb kód (3 sor vs 7 sor)
- ✅ Olvashatóbb (szemantikus függvénynév)
- ✅ Újrafelhasználható (más transform-ok is használhatják)
- ✅ Központosított logika (egy helyen változtatható)

## Format Config Példa

A helper-ek közvetlenül is használhatók a format config-ban:

```json
{
  "mappings": {
    "{{INFO_BOX_CONTENT}}": {
      "source": "chapters.ch01.info_box.fields",
      "pipeline": [
        {"transform": "make_info_box_content"}
      ]
    }
  }
}
```

## Architektúra

```
labor/transforms/
├── __init__.py                  # Export registry + helpers
├── registry.py                  # TransformRegistry osztály
├── formatting_helpers.py        # Újrafelhasználható inline array helper-ek
├── common_transforms.py         # Általános transform-ok (join, case)
├── qms_transforms.py            # QMS-specifikus transform-ok
└── calibration_transforms.py   # Kalibrálás-specifikus transform-ok (opcionális)
```

## Best Practices

1. **Helper használat**: Ha inline array-t kell generálni, először nézd meg van-e rá helper
2. **DRY principle**: Ne ismételd az inline array generálás logikát, használj helper-t
3. **Szemantikus elnevezés**: A helper függvénynevek mondják el mit csinálnak
4. **Dokumentáció**: Minden helper docstring-gel és példával van dokumentálva
5. **Tesztelés**: Minden új helper-hez írj unit tesztet

## Teljes Példa: QMS Pipeline

```python
# 1. Build QMS
from qms.build_qms import main as build_qms
build_qms()

# 2. Convert QMS (használja a transform-okat és helper-eket)
from converters import QMSConverter
converter = QMSConverter()
docjl = converter.convert(
    'qms/build/QMS_full_input.json',
    'qms/build/QMS_full_template.json',
    'qms/build/QMS_full_format.json'
)

# 3. Generate LaTeX
from docjl import MarkdownJsonToDocjl
latex_converter = MarkdownJsonToDocjl()
latex = latex_converter.convert(json.dumps(docjl))

# 4. LaTeX → PDF
# pdflatex qms_manual.tex
```

## Verzió Történet

- **v2.1.0** - Helper-ek hozzáadása (2025-10-19)
  - `formatting_helpers.py` létrehozása
  - QMS transform-ok refaktorálása helper használattal
  - Export helper-ek a package-ből
- **v2.0.0** - Transform Registry és plugin architektúra
- **v1.0.0** - Kezdeti QMS transform-ok

## Licensz

MIT License - PeTitan Informatika Kft. 2025
