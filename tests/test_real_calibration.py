"""Integration test with real calibration data."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

# Test data paths
TEMPLATE_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_template.json"
LATEX_DIR = Path(__file__).parent.parent / "latex"


def create_real_calibration_data() -> dict:
    """Create a realistic calibration procedure with real data.

    Example: Pressure Gauge Calibration Procedure
    """
    return {
        "docjll": [
            {"type": "heading", "level": 1, "content": "M-01 - Nyomásmérő kalibrálási eljárás"},
            {
                "type": "table",
                "headers": ["Mező", "Érték"],
                "rows": [
                    ["Eljárás kódja:", "PET-KAL-M-01"],
                    ["Eljárás címe:", "Analóg nyomásmérők kalibrálása"],
                    ["Mérési tartomány:", "0 - 10 bar"],
                    ["Pontossági követelmény:", "±0.5% teljes skála"],
                    ["Verzió:", "2.1"],
                    ["Hatályba lépés:", "2025-01-15"],
                    ["Hivatkozások:", "ISO/IEC 17025:2018, MSZ EN 837-1:2003"],
                    ["Jóváhagyta:", "Dr. Kovács János (Minőségügyi vezető)"],
                ],
                "caption": "Eljárás alapadatok",
            },
            {"type": "heading", "level": 2, "content": "1. A kalibrálási eljárás hatálya"},
            {"type": "heading", "level": 3, "content": "1.1 Kalibrálandó mérőberendezés"},
            {
                "type": "paragraph",
                "content": "Jelen eljárás analóg nyomásmérő műszerek kalibrálására vonatkozik, amelyek mechanikus mutatóval rendelkeznek és 0-10 bar mérési tartományban működnek.",
            },
            {"type": "paragraph", "content": [{"type": "bold", "content": "Mérési tartományok:"}]},
            {
                "type": "list_unordered",
                "items": [
                    "0 - 1 bar (finommechanikai alkalmazások)",
                    "0 - 6 bar (hidraulikus rendszerek)",
                    "0 - 10 bar (pneumatikus rendszerek)",
                ],
            },
            {"type": "heading", "level": 3, "content": "1.2 Eljárás típusa és alkalmazhatóság"},
            {
                "type": "paragraph",
                "content": [
                    {"type": "bold", "content": "Eljárás típusa: "},
                    {
                        "type": "text",
                        "content": "Összehasonlító mérés referencia nyomásstandard alkalmazásával",
                    },
                ],
            },
            {"type": "paragraph", "content": [{"type": "bold", "content": "Alkalmazható:"}]},
            {
                "type": "list_unordered",
                "items": [
                    "Bourdon csöves nyomásmérők",
                    "Membránkapszulás nyomásmérők",
                    "Ipari pontossági osztályú műszerek (1.0, 1.6, 2.5 osztály)",
                ],
            },
            {"type": "paragraph", "content": [{"type": "bold", "content": "Nem alkalmazható:"}]},
            {
                "type": "list_unordered",
                "items": [
                    "Digitális nyomásmérők (lásd: PET-KAL-M-02)",
                    "Precíziós referencia műszerek (lásd: PET-KAL-M-03)",
                ],
            },
            {"type": "heading", "level": 3, "content": "1.3 Működési elv"},
            {
                "type": "paragraph",
                "content": "A kalibrálás során a kalibrálandó műszert és a referencia nyomásstandard-ot azonos nyomású közegre csatlakoztatjuk. A két műszer által mutatott értékek különbsége adja a kalibrálandó műszer hibáját.",
            },
            {"type": "heading", "level": 2, "content": "2. A kalibrálási/mérési elv"},
            {"type": "heading", "level": 3, "content": "2.1 Kalibrálási módszer"},
            {
                "type": "paragraph",
                "content": "A kalibrálást összehasonlító módszerrel végezzük precíziós nyomáskalibrátorral. A műszert a skála 0%, 20%, 40%, 60%, 80% és 100% pontjain kalibráljuk, növekvő és csökkenő irányban is.",
            },
            {"type": "paragraph", "content": [{"type": "bold", "content": "Mérés egyenlete:"}]},
            {
                "type": "equation",
                "content": "\\Delta p = p_{\\text{mért}} - p_{\\text{ref}}",
                "label": "eq:meres",
            },
            {"type": "paragraph", "content": "ahol:"},
            {
                "type": "list_unordered",
                "items": [
                    [
                        {"type": "math", "content": "\\Delta p"},
                        {"type": "text", "content": " -- a műszer hibája [bar]"},
                    ],
                    [
                        {"type": "math", "content": "p_{\\text{mért}}"},
                        {"type": "text", "content": " -- a kalibrálandó műszer leolvasása [bar]"},
                    ],
                    [
                        {"type": "math", "content": "p_{\\text{ref}}"},
                        {"type": "text", "content": " -- a referencia standard értéke [bar]"},
                    ],
                ],
            },
            {"type": "heading", "level": 3, "content": "2.2 Befolyásoló mennyiségek"},
            {
                "type": "list_unordered",
                "items": [
                    [
                        {"type": "bold", "content": "Hőmérséklet: "},
                        {"type": "text", "content": "±0.01 bar/°C"},
                    ],
                    [
                        {"type": "bold", "content": "Légnyomás: "},
                        {
                            "type": "text",
                            "content": "elhanyagolható hatás relatív nyomásmérés esetén",
                        },
                    ],
                    [
                        {"type": "bold", "content": "Páratartalom: "},
                        {"type": "text", "content": "nincs közvetlen hatás"},
                    ],
                ],
            },
            {
                "type": "heading",
                "level": 2,
                "content": "3. A kalibrálással meghatározandó metrológiai jellemzők",
            },
            {
                "type": "paragraph",
                "content": "Mérési hiba minden mérési ponton, hiszterézis, ismételhetőség, lineáris regresszió paraméterei.",
            },
            {
                "type": "heading",
                "level": 2,
                "content": "4. Jelölések, mértékegységek és meghatározások",
            },
            {"type": "heading", "level": 3, "content": "4.1 Jelölések és mértékegységek"},
            {
                "type": "table",
                "headers": ["Megnevezés", "Jelölés", "Mértékegység"],
                "rows": [
                    ["Referencia nyomás", "$p_{\\text{ref}}$", "bar"],
                    ["Mért nyomás", "$p_{\\text{mért}}$", "bar"],
                    ["Mérési hiba", "$\\Delta p$", "bar"],
                    ["Bővített mérési bizonytalanság", "$U$", "bar"],
                    ["Hisztérézis", "$H$", "bar"],
                ],
                "caption": "Jelölések és mértékegységek",
            },
            {"type": "heading", "level": 2, "content": "5. Berendezések"},
            {"type": "heading", "level": 3, "content": "5.1 Etalonok és anyagminták"},
            {
                "type": "paragraph",
                "content": "Fluke 719Pro precíziós nyomáskalibrátor, széria: 12345678, pontosság: ±0.025% FS, érvényes kalibrálás: 2024-12-15",
            },
            {"type": "heading", "level": 3, "content": "5.2 Egyéb mérőeszközök"},
            {
                "type": "list_unordered",
                "items": ["Digitális hőmérő (±0.1°C)", "Digitális barométer (±0.5 hPa)"],
            },
            {"type": "heading", "level": 3, "content": "5.3 Segédeszközök"},
            {
                "type": "list_unordered",
                "items": ["T-elágazó csatlakozó (M20×1.5)", "PTFE tömítőszalag"],
            },
            {
                "type": "heading",
                "level": 2,
                "content": "6. Környezeti körülmények és stabilizálódási idő",
            },
            {"type": "heading", "level": 3, "content": "6.1 Környezeti követelmények"},
            {
                "type": "table",
                "headers": ["Paraméter", "Tartomány", "Megjegyzés"],
                "rows": [
                    ["Hőmérséklet", "20 -- 24°C", "Folyamatos monitoring szükséges"],
                    ["Relatív páratartalom", "30 -- 70%", "Kondenzációmentes"],
                ],
                "caption": "Környezeti paraméterek",
            },
            {"type": "heading", "level": 3, "content": "6.2 Stabilizálódási idő"},
            {
                "type": "paragraph",
                "content": "A műszereket minimum 2 órán át a laboratóriumi környezetben kell hagyni a hőmérsékleti egyensúly elérése érdekében.",
            },
            {"type": "heading", "level": 2, "content": "7. Átvétel és előkészítés"},
            {"type": "heading", "level": 3, "content": "7.1 Átvételi feltételek"},
            {
                "type": "paragraph",
                "content": "Ellenőrizni kell a műszer épségét, az üveg sértetlenségét, a csatlakozó menetek állapotát.",
            },
            {"type": "heading", "level": 3, "content": "7.2 Jelölés és nyilvántartásba vétel"},
            {
                "type": "paragraph",
                "content": "A műszert egyedi azonosítóval látjuk el a LIMS rendszerben.",
            },
            {
                "type": "heading",
                "level": 3,
                "content": "7.3 Előkészítés és működőképesség ellenőrzése",
            },
            {
                "type": "paragraph",
                "content": "Vizuális ellenőrzés, nulla pont ellenőrzése, mechanikus sérülések kizárása.",
            },
            {"type": "heading", "level": 3, "content": "7.4 Etalonok előkészítése"},
            {
                "type": "paragraph",
                "content": "A Fluke 719Pro kalibrátort 30 perccel a mérés előtt be kell kapcsolni a belső referencia stabilizálódása érdekében.",
            },
            {"type": "heading", "level": 3, "content": "7.5 Biztonsági intézkedések"},
            {
                "type": "paragraph",
                "content": "A pneumatikus rendszer nyomását fokozatosan kell növelni és csökkenteni. 10 bar feletti nyomás esetén védőpajzs használata kötelező.",
            },
            {"type": "heading", "level": 2, "content": "8. Kalibrálás/mérés"},
            {"type": "heading", "level": 3, "content": "8.1 Műveleti sorrend"},
            {
                "type": "paragraph",
                "content": "1. Műszerek csatlakoztatása, 2. Nulla pont ellenőrzése, 3. Növekvő ciklus (0-100%), 4. Csökkenő ciklus (100-0%), 5. Adatok rögzítése.",
            },
            {"type": "heading", "level": 3, "content": "8.2 Metrológiai jellemzők kiszámítása"},
            {
                "type": "paragraph",
                "content": "A mérési hibát minden ponton kiszámítjuk a referencia és mért értékek különbségeként. A hisztérézist a növekvő és csökkenő ciklus közötti maximális eltérés adja.",
            },
            {"type": "heading", "level": 3, "content": "8.3 Mérési bizonytalanság meghatározása"},
            {
                "type": "paragraph",
                "content": "A bizonytalanságot az EA-4/02 útmutató szerint számítjuk, figyelembe véve a referencia bizonytalanságát, a leolvasás bizonytalanságát, a hiszterézist és a hőmérsékleti hatást.",
            },
            {
                "type": "table",
                "headers": [
                    "Bizonytalansági forrás",
                    "Érték u(x)",
                    "Eloszlás",
                    "Érzékenység c",
                    "Járulék c·u(x)",
                ],
                "rows": [
                    ["Referencia standard", "0.0025 bar", "normál", "1.0", "0.0025 bar"],
                    ["Leolvasási felbontás", "0.0029 bar", "egyenletes", "1.0", "0.0029 bar"],
                    ["Hisztérézis", "0.0100 bar", "egyenletes", "0.58", "0.0058 bar"],
                    ["Hőmérséklet hatás", "0.0200 bar", "egyenletes", "0.5", "0.0100 bar"],
                ],
                "caption": "Bizonytalansági komponensek - 10 bar mérési pont",
                "note": "Összetett standard bizonytalanság: 0.012 bar, k=2, U=0.024 bar",
            },
            {
                "type": "table",
                "headers": ["Paraméter", "Érték"],
                "rows": [
                    ["Szabadságfok", "$\\nu_{\\text{eff}} = 50$"],
                    ["Bővítési tényező", "$k = 2.00$"],
                    ["Bővített bizonytalanság (95%)", "$U = 0.024$ bar"],
                ],
                "caption": "KMK meghatározás",
            },
            {"type": "heading", "level": 3, "content": "8.4 Minősítés (megfelelőségértékelés)"},
            {
                "type": "paragraph",
                "content": "A műszer megfelelő, ha a mérési hiba minden ponton kisebb, mint a specifikált pontossági osztály szerint megengedett hiba.",
            },
            {"type": "heading", "level": 2, "content": "9. Az eredmények közlése"},
            {
                "type": "paragraph",
                "content": "Az eredményeket a PET-KAL-J-01 kalibrálási jegyzőkönyv formátumban adjuk ki, amely tartalmazza a mérési hibákat, a bizonytalanságot és a megfelelőségi nyilatkozatot.",
            },
            {
                "type": "table",
                "headers": ["Mérési pont", "Eredmény"],
                "rows": [
                    ["0.0 bar (0%)", "$\\Delta p = 0.00 \\pm 0.02$ bar"],
                    ["2.0 bar (20%)", "$\\Delta p = -0.03 \\pm 0.02$ bar"],
                    ["4.0 bar (40%)", "$\\Delta p = -0.05 \\pm 0.02$ bar"],
                    ["6.0 bar (60%)", "$\\Delta p = -0.04 \\pm 0.02$ bar"],
                    ["8.0 bar (80%)", "$\\Delta p = -0.02 \\pm 0.02$ bar"],
                    ["10.0 bar (100%)", "$\\Delta p = 0.00 \\pm 0.02$ bar"],
                ],
                "caption": "Kalibrálási eredmények -- Példa nyomásmérő S/N: 2024-001",
            },
            {"type": "heading", "level": 2, "content": "10. A kalibrálási eljárás validálása"},
            {
                "type": "paragraph",
                "content": [{"type": "bold", "content": "Validálási nyilatkozat"}],
            },
            {
                "type": "paragraph",
                "content": "Jelen eljárást 2024. december 10-én validáltuk egy ismert hibájú referencia műszerrel. A mért hiba 0.032 bar volt, a várt hiba 0.030 bar, az eltérés a mérési bizonytalanságon belül van.",
            },
            {
                "type": "table",
                "headers": ["Kritérium", "Követelmény", "Teljesítés"],
                "rows": [
                    ["Mérési bizonytalanság", "$U < 0.05$ bar", "✓ MEGFELEL ($U = 0.024$ bar)"],
                    ["Ismételhetőség", "$s < 0.01$ bar", "✓ MEGFELEL ($s = 0.005$ bar)"],
                    ["Referencia érvényesség", "Érvényes kalibrálás", "✓ MEGFELEL (2024-12-15)"],
                ],
                "caption": "Validálási elfogadási kritériumok",
            },
        ]
    }


class TestRealCalibrationData:
    """Integration tests with real calibration procedure data."""

    def test_generate_pdf_with_real_data(self):
        """Test complete workflow: real data -> JSON -> LaTeX -> PDF."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed")

        # Check pdflatex
        if subprocess.run(["which", "pdflatex"], capture_output=True).returncode != 0:
            pytest.skip("pdflatex not installed")

        # Get real calibration data
        real_data = create_real_calibration_data()
        real_json = json.dumps(real_data, ensure_ascii=False, indent=2)

        # Convert to LaTeX
        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(real_json)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "real_calibration.tex"
            pdf_file = tmpdir_path / "real_calibration.pdf"

            # Write LaTeX
            tex_file.write_text(latex_output, encoding="utf-8")

            # Set up environment for custom LaTeX class
            env = os.environ.copy()
            if LATEX_DIR.exists():
                env["TEXINPUTS"] = f"{LATEX_DIR}:{env.get('TEXINPUTS', '')}"

            # Compile to PDF (two passes for references)
            for _ in range(2):
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=30,
                    env=env,
                )

            # Check PDF was created
            assert pdf_file.exists(), "PDF generation failed"
            assert pdf_file.stat().st_size > 10000, "PDF is too small"

            # Copy PDF to project root for inspection
            output_pdf = Path(__file__).parent.parent / "real_calibration_output.pdf"
            import shutil

            shutil.copy(pdf_file, output_pdf)

            print(f"\n✓ Real calibration PDF generated: {output_pdf}")
            print(f"  Size: {output_pdf.stat().st_size} bytes")

    def test_real_data_structure(self):
        """Test that real data has valid structure."""
        real_data = create_real_calibration_data()

        assert "docjll" in real_data
        assert isinstance(real_data["docjll"], list)
        assert len(real_data["docjll"]) > 0

        # Check for key sections
        content = json.dumps(real_data, ensure_ascii=False)
        assert "Nyomásmérő kalibrálási eljárás" in content
        assert "PET-KAL-M-01" in content
        assert "Fluke 719Pro" in content
        assert "ISO/IEC 17025:2018" in content

    def test_real_data_has_complete_workflow(self):
        """Test that real data includes complete calibration workflow."""
        real_data = create_real_calibration_data()
        content = json.dumps(real_data, ensure_ascii=False)

        # Check all required sections are present
        required_sections = [
            "hatálya",
            "mérési elv",
            "metrológiai jellemzők",
            "Jelölések",
            "Berendezések",
            "Környezeti",
            "Átvétel",
            "Kalibrálás/mérés",
            "eredmények közlése",
            "validálása",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_real_data_has_equations(self):
        """Test that real data includes calibration equations."""
        real_data = create_real_calibration_data()

        # Find equation blocks
        equations = [block for block in real_data["docjll"] if block.get("type") == "equation"]

        assert len(equations) > 0, "No equations found"
        assert "Delta p" in equations[0]["content"], "Equation content missing"

    def test_real_data_has_tables(self):
        """Test that real data includes measurement tables."""
        real_data = create_real_calibration_data()

        # Find table blocks
        tables = [block for block in real_data["docjll"] if block.get("type") == "table"]

        assert len(tables) >= 4, f"Expected at least 4 tables, found {len(tables)}"

        # Check for uncertainty budget table
        uncertainty_table = None
        for table in tables:
            if "Bizonytalansági" in table.get("caption", ""):
                uncertainty_table = table
                break

        assert uncertainty_table is not None, "Uncertainty budget table not found"
        assert len(uncertainty_table["rows"]) >= 3, "Uncertainty table has too few rows"

    def test_real_data_has_results(self):
        """Test that real data includes measurement results."""
        real_data = create_real_calibration_data()

        # Find results table
        results_table = None
        for block in real_data["docjll"]:
            if block.get("type") == "table" and "eredmények" in block.get("caption", ""):
                results_table = block
                break

        assert results_table is not None, "Results table not found"
        assert len(results_table["rows"]) == 6, "Should have 6 measurement points"

        # Check that results contain measurement data
        first_result = results_table["rows"][0][1]
        assert (
            "Delta p" in first_result or "pm" in first_result
        ), "Results should contain measurement data"
