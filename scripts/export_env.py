"""Export environment package versions for reproducibility.
Outputs:
- requirements-frozen.txt (pip style)
- environment-lock.json (structured)
Usage: python scripts/export_env.py
"""
import json
import pkg_resources
from datetime import datetime


def collect_packages():
    packages = []
    for dist in pkg_resources.working_set:
        packages.append({"name": dist.project_name, "version": dist.version})
    packages.sort(key=lambda x: x["name"].lower())
    return packages


def write_requirements_txt(packages):
    with open("requirements-frozen.txt", "w", encoding="utf-8") as f:
        for p in packages:
            f.write(f"{p['name']}=={p['version']}\n")


def write_lock_json(packages):
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tool": "export_env.py",
        "count": len(packages),
        "packages": packages,
    }
    with open("environment-lock.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    packages = collect_packages()
    write_requirements_txt(packages)
    write_lock_json(packages)
    print(f"Exported {len(packages)} packages.")

if __name__ == "__main__":
    main()
