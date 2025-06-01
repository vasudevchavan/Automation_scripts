import re
import configparser
from pathlib import Path
import toml
import yaml

def extract_from_requirements(file_path):
    packages = set()
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                pkg = re.split(r'[<=>~!]', line)[0].strip()
                if pkg:
                    packages.add(pkg.lower())
    return packages

def extract_from_setup_py(file_path):
    packages = set()
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    install_requires = re.findall(r'install_requires\s*=\s*\[([^\]]+)\]', content, re.DOTALL)
    if install_requires:
        raw = install_requires[0]
        entries = re.findall(r'["\']([^"\']+)["\']', raw)
        for entry in entries:
            pkg = re.split(r'[<=>~!]', entry)[0].strip()
            if pkg:
                packages.add(pkg.lower())
    return packages

def extract_from_pyproject(file_path):
    packages = set()
    try:
        data = toml.load(file_path)
    except Exception:
        return packages
    if 'project' in data and 'dependencies' in data['project']:
        for dep in data['project']['dependencies']:
            pkg = re.split(r'[<=>~!]', dep)[0].strip()
            if pkg:
                packages.add(pkg.lower())
    poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
    for pkg, spec in poetry_deps.items():
        if pkg.lower() != 'python':
            packages.add(pkg.lower())
    return packages

def extract_from_setup_cfg(file_path):
    packages = set()
    config = configparser.ConfigParser()
    config.read(file_path)
    if 'options' in config and 'install_requires' in config['options']:
        deps = config['options']['install_requires'].strip().splitlines()
        for dep in deps:
            pkg = re.split(r'[<=>~!]', dep.strip())[0]
            if pkg:
                packages.add(pkg.lower())
    return packages

def extract_from_pipfile(file_path):
    packages = set()
    try:
        data = toml.load(file_path)
        deps = data.get('packages', {})
        for pkg in deps:
            packages.add(pkg.lower())
    except Exception:
        pass
    return packages

def extract_from_environment_yml(file_path):
    packages = set()
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if 'dependencies' in data:
                for dep in data['dependencies']:
                    if isinstance(dep, str):
                        pkg = re.split(r'[<=>~!]', dep)[0].strip()
                        packages.add(pkg.lower())
                    elif isinstance(dep, dict) and 'pip' in dep:
                        for pip_pkg in dep['pip']:
                            pkg = re.split(r'[<=>~!]', pip_pkg)[0].strip()
                            packages.add(pkg.lower())
    except Exception:
        pass
    return packages

def extract_from_tox_ini(file_path):
    packages = set()
    config = configparser.ConfigParser()
    config.read(file_path)
    for section in config.sections():
        if section.startswith('testenv') and 'deps' in config[section]:
            deps = config[section]['deps'].strip().splitlines()
            for dep in deps:
                dep = dep.strip()
                if dep and not dep.startswith('{'):
                    pkg = re.split(r'[<=>~!]', dep)[0]
                    if pkg:
                        packages.add(pkg.lower())
    return packages

def scan_all_dependency_files(root_path='.'):
    all_packages = set()
    root = Path(root_path)

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        name = file_path.name

        try:
            if name == 'requirements.txt' or name.endswith('-requirements.txt'):
                all_packages |= extract_from_requirements(file_path)
            elif name == 'setup.py':
                all_packages |= extract_from_setup_py(file_path)
            elif name == 'pyproject.toml':
                all_packages |= extract_from_pyproject(file_path)
            elif name == 'setup.cfg':
                all_packages |= extract_from_setup_cfg(file_path)
            elif name == 'Pipfile':
                all_packages |= extract_from_pipfile(file_path)
            elif name == 'environment.yml':
                all_packages |= extract_from_environment_yml(file_path)
            elif name == 'tox.ini':
                all_packages |= extract_from_tox_ini(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return all_packages

if __name__ == '__main__':
    packages = scan_all_dependency_files()
    print("\n📦 Found Python packages:")
    for pkg in sorted(packages):
        print(f"- {pkg}")
