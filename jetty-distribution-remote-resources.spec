Name:           jetty-distribution-remote-resources
Version:        1.2
Release:        1
Summary:        Jetty toolchain artifact for distribution remote resources

License:        ASL 2.0 or EPL
URL:            https://www.eclipse.org/jetty/
Source0:        https://github.com/jetty/jetty.toolchain/archive/refs/tags/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:	python
BuildSystem:	maven

Requires:       javapackages-filesystem

%description
Jetty toolchain artifact for distribution remote distribution resources

%prep
%setup -q -n jetty-toolchain-%{name}-%{version}
# The tag is the whole toolchain reactor. Publish this module on its own.
python - <<'PY'
import re
import shutil
from pathlib import Path
root = Path(".").resolve()
mod = root / "%{name}"
if mod.is_dir():
    stage = root.parent / ("%{name}-module")
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(mod, stage)
    for child in list(root.iterdir()):
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for child in list(stage.iterdir()):
        shutil.move(str(child), root / child.name)
    shutil.rmtree(stage)
path = root / "pom.xml"
text = path.read_text()
text = re.sub(r"\s*<parent>.*?</parent>", "", text, count=1, flags=re.S)
head, sep, tail = text.partition("<artifactId>")
if sep and "<groupId>" not in head:
    text = head + "<groupId>org.eclipse.jetty.toolchain</groupId>\n  " + sep + tail
path.write_text(text)
PY

%files -f .mfiles
%doc src/main/resources/license-eplv10-aslv20.html src/main/resources/notice.html
