Name:           jetty-distribution-remote-resources
Version:        1.2
Release:        1
Summary:        Jetty toolchain artifact for distribution remote resources
Group:          Development/Java
License:        ASL 2.0 or EPL
URL:            https://www.eclipse.org/jetty/
Source0:        https://github.com/jetty/jetty.toolchain/archive/refs/tags/%{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
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
# The remote-resources plugin is not packaged. The jar still has to carry
# the bundle index that plugin would have written.
python - <<'PY'
from pathlib import Path
root = Path("src/main/resources")
names = sorted(
    path.relative_to(root).as_posix()
    for path in root.rglob("*")
    if path.is_file()
)
dest = root / "META-INF" / "maven"
dest.mkdir(parents=True, exist_ok=True)
items = "\n".join(f"    <remoteResource>{name}</remoteResource>" for name in names)
(dest / "remote-resources.xml").write_text(
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    "<remoteResourcesBundle xmlns=\"http://maven.apache.org/remote-resources/1.1.0\">\n"
    "  <remoteResources>\n"
    + items + "\n"
    "  </remoteResources>\n"
    "</remoteResourcesBundle>\n"
)
PY

%files -f .mfiles
%doc src/main/resources/license-eplv10-aslv20.html src/main/resources/notice.html
