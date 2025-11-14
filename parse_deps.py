import re

# Read both lockfiles
with open('/tmp/uv.lock.old', 'r') as f:
    old_content = f.read()

with open('uv.lock', 'r') as f:
    new_content = f.read()

# Extract package versions using regex
package_pattern = r'\[\[package\]\]\s+name = "([^"]+)"[^\[]*?version = "([^"]+)"'

old_packages = {name: version for name, version in re.findall(package_pattern, old_content)}
new_packages = {name: version for name, version in re.findall(package_pattern, new_content)}

# Categorize changes
updated = []
added = []
removed = []

for name, new_ver in sorted(new_packages.items()):
    if name in old_packages:
        old_ver = old_packages[name]
        if old_ver != new_ver:
            updated.append(f"- {name}: {old_ver} → {new_ver}")
    else:
        added.append(f"- {name}: {new_ver}")

for name, old_ver in sorted(old_packages.items()):
    if name not in new_packages:
        removed.append(f"- {name}: {old_ver}")

# Generate summary
summary = "### Updated\n"
summary += "\n".join(updated) if updated else "(none)"
summary += "\n\n### Added\n"
summary += "\n".join(added) if added else "(none)"
summary += "\n\n### Removed\n"
summary += "\n".join(removed) if removed else "(none)"

# Write to file
with open('dependency-summary.txt', 'w') as f:
    f.write(summary)
