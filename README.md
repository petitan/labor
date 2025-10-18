# Labor

Professzionális Python CLI alkalmazás fejlesztői környezettel.

## Telepítés

### 1. Python 3.12 ellenőrzése

```bash
python3.12 --version
```

### 2. Virtual environment létrehozása

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# vagy
venv\Scripts\activate  # Windows
```

### 3. Függőségek telepítése

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Pre-commit hooks telepítése

```bash
pre-commit install
```

## Fejlesztői eszközök

### Kód formázás és linting

```bash
# Ruff linting
ruff check .

# Automatikus javítás
ruff check --fix .

# Kód formázás
ruff format .
```

### Type checking

```bash
# MyPy type checking
mypy src
```

### Tesztek futtatása

```bash
# Összes teszt futtatása
pytest

# Coverage reporttal
pytest --cov

# HTML coverage report
pytest --cov --cov-report=html
# Megnyitás: open htmlcov/index.html
```

### Pre-commit hooks manuális futtatása

```bash
# Összes hook futtatása minden fájlon
pre-commit run --all-files

# Egy adott hook futtatása
pre-commit run ruff --all-files
```

## Projekt struktúra

```
labor/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI/CD
├── .vscode/
│   ├── settings.json       # VS Code beállítások
│   └── extensions.json     # Ajánlott VS Code extensionök
├── src/
│   └── labor/
│       ├── __init__.py
│       └── main.py         # Fő alkalmazás logika
├── tests/
│   ├── __init__.py
│   └── test_main.py        # Unit tesztek
├── .gitignore
├── .pre-commit-config.yaml # Pre-commit hooks konfig
├── pyproject.toml          # Projekt és tool konfigurációk
├── requirements.txt        # Production függőségek
├── requirements-dev.txt    # Development függőségek
└── README.md
```

## Használat

```bash
# Alkalmazás futtatása
python -m labor.main

# Vagy a venv aktiválása után
python src/labor/main.py
```

## CI/CD

A projekt GitHub Actions-t használ automata tesztelésre és minőségellenőrzésre:

- Ruff linting és formázás ellenőrzés
- MyPy type checking
- Pytest unit tesztek coverage reporttal
- Codecov integráció

## VS Code ajánlott extensionök

A projekt automatikusan ajánlja a következő VS Code extensionöket:

- Python (Microsoft)
- Pylance (Microsoft)
- Ruff (Astral Software)
- Even Better TOML
- GitHub Actions

## Licensz

MIT
