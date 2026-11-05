Name:		javax-activation
Version:	1.2.0
Release:	1
Summary:	JavaBeans Activation Framework
Group:		Development/Java
License:	CDDL-1.1 OR GPL-2.0-only WITH Classpath-exception-2.0
URL:		https://github.com/eclipse-ee4j/jaf
Source0:	https://repo1.maven.org/maven2/com/sun/activation/javax.activation/%{version}/javax.activation-%{version}-sources.jar
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name javax.activation --alias javax.activation:activation --alias javax.activation:javax.activation-api --alias org.apache.geronimo.specs:geronimo-activation_1.1_spec

%description
JavaBeans Activation Framework 1.2. The packages are still
javax.activation. Jakarta Activation 2.0 renamed them.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
mkdir -p src/main/java src/main/resources/META-INF
mv javax com src/main/java/
mv META-INF/mailcap.default META-INF/mimetypes.default src/main/resources/META-INF/
cp -a META-INF/LICENSE.txt LICENSE.txt
python - %{version} <<'PY'
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
version = sys.argv[1]
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def local(tag):
    return tag.split("}", 1)[-1]

tree = ET.parse("pom.xml")
root = tree.getroot()
for node in list(root):
    if local(node.tag) == "parent":
        root.remove(node)
if not any(local(node.tag) == "version" for node in root):
    version_node = ET.Element(f"{{{NS}}}version")
    version_node.text = version
    inserted = False
    for index, node in enumerate(list(root)):
        if local(node.tag) == "artifactId":
            root.insert(index + 1, version_node)
            inserted = True
            break
    if not inserted:
        root.append(version_node)
# The parent is not packaged. Drop plugin config that only existed to
# fork a Java 5 compile.
for node in list(root):
    if local(node.tag) == "build":
        root.remove(node)
tree.write("pom.xml", encoding="utf-8", xml_declaration=True)
PY

%files -f .mfiles
%doc LICENSE.txt
