"""Static checks enforcing the documented dependency rule: domain is
innermost, and every package's __init__.py is the sole import surface
for its consumers — nothing reaches past it into a submodule."""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "life"

_PEER_LAYERS = ("seeds", "engines", "infrastructure", "presentation", "simulation")
_DEEP_DOMAIN_MODULES = ("life.domain.types", "life.domain.protocols", "life.domain.rules")
_DEEP_VALIDATION_MODULES = ("life.validation.exceptions",)


def _imported_modules(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text(), filename=str(file_path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
    return modules


def _all_python_files(*roots: Path) -> list[Path]:
    files = []
    for root in roots:
        files.extend(root.rglob("*.py"))
    return files


class TestValidationDependencies:
    def test_validation_does_not_import_peer_layers(self):
        for file_path in (SRC / "validation").glob("*.py"):
            modules = _imported_modules(file_path)
            offending = {
                m for m in modules
                if any(m.startswith(f"life.{layer}") for layer in _PEER_LAYERS)
            }
            assert not offending, f"{file_path} imports peer layers: {offending}"


class TestSeedRegistrySync:
    def test_seed_registry_matches_built_in_seeds(self):
        from life.domain import BUILT_IN_SEEDS
        from life.seeds import SEED_REGISTRY
        assert set(SEED_REGISTRY.keys()) == BUILT_IN_SEEDS


class TestFacadesAreTheOnlyImportSurface:
    def test_no_file_outside_domain_imports_domain_submodules_directly(self):
        tests_dir = Path(__file__).resolve().parent
        for file_path in _all_python_files(SRC, tests_dir):
            if file_path.is_relative_to(SRC / "domain"):
                continue
            modules = _imported_modules(file_path)
            offending = modules & set(_DEEP_DOMAIN_MODULES)
            assert not offending, f"{file_path} imports domain submodules directly: {offending}"

    def test_no_file_outside_validation_imports_exceptions_module_directly(self):
        tests_dir = Path(__file__).resolve().parent
        for file_path in _all_python_files(SRC, tests_dir):
            if file_path.is_relative_to(SRC / "validation"):
                continue
            modules = _imported_modules(file_path)
            offending = modules & set(_DEEP_VALIDATION_MODULES)
            assert not offending, f"{file_path} imports life.validation.exceptions directly: {offending}"
