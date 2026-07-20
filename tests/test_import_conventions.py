"""Static checks enforcing the documented dependency rule: domain is
innermost, and validation must not depend on peer layers directly."""
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "life"

_PEER_LAYERS = ("seeds", "engines", "infrastructure", "presentation", "simulation")


def _imported_modules(file_path: Path) -> set[str]:
    tree = ast.parse(file_path.read_text(), filename=str(file_path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
    return modules


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
        from life.domain.types import BUILT_IN_SEEDS
        from life.seeds import SEED_REGISTRY
        assert set(SEED_REGISTRY.keys()) == BUILT_IN_SEEDS
