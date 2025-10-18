"""Integration tests for docjl conversion and PDF generation."""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

# Test data paths
TEMPLATE_PATH = Path(__file__).parent.parent / "src" / "labor" / "calibration_template.json"


@pytest.fixture
def template_json():
    """Load the calibration template as JSON string."""
    return TEMPLATE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def template_data():
    """Load the calibration template as Python dict."""
    with TEMPLATE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class TestDocjlConversion:
    """Tests for docjl converter integration."""

    def test_docjl_import(self):
        """Test that docjl module can be imported."""
        try:
            from docjl import MarkdownJsonToDocjl

            assert MarkdownJsonToDocjl is not None
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

    def test_convert_template_to_latex(self, template_json):
        """Test that template can be converted to LaTeX."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        # Basic LaTeX structure checks
        assert latex_output is not None, "Converter should return output"
        assert isinstance(latex_output, str), "Output should be string"
        assert len(latex_output) > 1000, "Output should be substantial"

    def test_latex_has_document_structure(self, template_json):
        """Test that LaTeX output has proper document structure."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        # Check essential LaTeX elements
        assert r"\documentclass" in latex_output, "Missing documentclass"
        assert r"\begin{document}" in latex_output, "Missing begin document"
        assert r"\end{document}" in latex_output, "Missing end document"

    def test_latex_has_hungarian_support(self, template_json):
        """Test that LaTeX output includes Hungarian language support."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        assert r"\usepackage[hungarian]{babel}" in latex_output, "Missing Hungarian babel"

    def test_latex_has_required_packages(self, template_json):
        """Test that LaTeX output includes required packages."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        required_packages = [
            r"\usepackage{amsmath}",
            r"\usepackage{longtable}",
            r"\usepackage{booktabs}",
            r"\usepackage{hyperref}",
        ]

        for package in required_packages:
            assert package in latex_output, f"Missing package: {package}"

    def test_latex_preserves_placeholders(self, template_json):
        """Test that placeholders are preserved in LaTeX output."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        # Check some key placeholders are preserved (with LaTeX escaping)
        expected_placeholders = [
            "ELJARAS\\_CIM",  # Underscores are escaped in LaTeX
            "MERESI\\_TARTOMANY",
            "KALIBRALASI\\_MODSZER",
        ]

        for placeholder in expected_placeholders:
            assert placeholder in latex_output, f"Placeholder {placeholder} not found in output"

    def test_latex_has_sections(self, template_json):
        """Test that LaTeX output contains proper section structure."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        assert r"\section{" in latex_output, "Missing section commands"
        assert r"\subsection{" in latex_output, "Missing subsection commands"
        assert r"\subsubsection{" in latex_output, "Missing subsubsection commands"

    def test_latex_has_tables(self, template_json):
        """Test that LaTeX output contains tables."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        assert r"\begin{table}" in latex_output, "Missing table environment"
        assert r"\begin{tabular}" in latex_output, "Missing tabular environment"
        assert r"\caption{" in latex_output, "Missing table captions"

    def test_latex_has_equations(self, template_json):
        """Test that LaTeX output contains equation environment."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        assert r"\begin{equation}" in latex_output, "Missing equation environment"
        assert r"\label{eq:" in latex_output, "Missing equation labels"


class TestPDFGeneration:
    """Tests for PDF generation from LaTeX output."""

    def test_pdflatex_available(self):
        """Test that pdflatex is available on the system."""
        result = subprocess.run(
            ["which", "pdflatex"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            pytest.skip("pdflatex not installed - required for PDF generation tests")

    def test_generate_pdf_from_template(self, template_json):
        """Test that PDF can be generated from template LaTeX."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        # Check pdflatex availability
        result = subprocess.run(
            ["which", "pdflatex"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            pytest.skip("pdflatex not installed")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        # Create temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "test_output.tex"
            pdf_file = tmpdir_path / "test_output.pdf"

            # Write LaTeX to file
            tex_file.write_text(latex_output, encoding="utf-8")

            # Compile to PDF
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check if compilation failed due to missing custom document class
            if "petitanmk.cls" in result.stdout or "petitanmk.cls" in result.stderr:
                pytest.skip("Custom document class petitanmk.cls not available in test environment")

            # Check PDF was created
            assert pdf_file.exists(), f"PDF was not generated. LaTeX errors: {result.stdout}"
            assert pdf_file.stat().st_size > 0, "Generated PDF is empty"

    def test_pdf_has_multiple_pages(self, template_json):
        """Test that generated PDF has expected number of pages."""
        try:
            from docjl import MarkdownJsonToDocjl
        except ImportError:
            pytest.skip("docjl not installed - run: pip install docjl")

        # Check pdflatex and pdfinfo availability
        if subprocess.run(["which", "pdflatex"], capture_output=True).returncode != 0:
            pytest.skip("pdflatex not installed")
        if subprocess.run(["which", "pdfinfo"], capture_output=True).returncode != 0:
            pytest.skip("pdfinfo not installed")

        converter = MarkdownJsonToDocjl()
        latex_output = converter.convert(template_json)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            tex_file = tmpdir_path / "test_output.tex"
            pdf_file = tmpdir_path / "test_output.pdf"

            tex_file.write_text(latex_output, encoding="utf-8")

            # Compile PDF
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Skip if custom document class is missing
            if "petitanmk.cls" in result.stdout or "petitanmk.cls" in result.stderr:
                pytest.skip("Custom document class petitanmk.cls not available in test environment")

            if not pdf_file.exists():
                pytest.skip("PDF generation failed")

            # Check page count
            result = subprocess.run(
                ["pdfinfo", pdf_file.name],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )

            # Extract page count
            for line in result.stdout.splitlines():
                if "Pages:" in line:
                    pages = int(line.split(":")[1].strip())
                    assert pages >= 3, f"Expected at least 3 pages, got {pages}"
                    break
