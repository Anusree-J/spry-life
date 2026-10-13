"""Package only approved public website files for GitHub Pages."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root / "site"
target = root / "dist"
expected = {"index.html", "style.css", "favicon.svg"}
assert {p.name for p in source.iterdir()} == expected
for name in expected:
    path = source / name
    assert path.is_file() and not path.is_symlink(), name
if target.exists():
    shutil.rmtree(target)
target.mkdir()
for name in expected:
    shutil.copyfile(source / name, target / name)
(target / ".nojekyll").touch()
print("Built dist: 3 public files, no dependencies or scripts")
