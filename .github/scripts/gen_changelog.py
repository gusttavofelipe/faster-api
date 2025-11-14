import tomllib
from pathlib import Path

OLD = Path("uv.lock.old")
NEW = Path("uv.lock")


def load_packages(path: Path):
	data = tomllib.loads(path.read_text())
	pkgs = {}
	for pkg in data.get("package", []):
		name = pkg["name"]
		version = pkg["version"]
		pkgs[name] = version
	return pkgs


old_pkgs = load_packages(OLD)
new_pkgs = load_packages(NEW)

updated = []
added = []
removed = []

for name, new_v in new_pkgs.items():
	old_v = old_pkgs.get(name)
	if old_v and old_v != new_v:
		updated.append((name, old_v, new_v))
	if not old_v:
		added.append((name, new_v))

for name, old_v in old_pkgs.items():
	if name not in new_pkgs:
		removed.append((name, old_v))

out = []

out.append("### Updated")
if updated:
	for name, old_v, new_v in sorted(updated):
		out.append(f"- {name}: {old_v} → {new_v}")
else:
	out.append("(none)")

out.append("\n### Added")
if added:
	for name, new_v in sorted(added):
		out.append(f"- {name}: {new_v}")
else:
	out.append("(none)")

out.append("\n### Removed")
if removed:
	for name, old_v in sorted(removed):
		out.append(f"- {name}")
else:
	out.append("(none)")

Path("CHANGELOG.update.md").write_text("\n".join(out))
