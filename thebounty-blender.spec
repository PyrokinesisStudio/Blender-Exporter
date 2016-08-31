Summary:            TheBounty plugin for blender.
Name:               thebounty-blender
Version:            0.1.6.rc4
Release:            5%{?dist}
License:            GPLv2+
Group:              Applications/Multimedia
Source0: 			https://github.com/TheBounty/Blender-Exporter/archive/%{version}.tar.gz
URL:                https://www.thebountyrenderer.org/
BuildArch:          noarch
BuildRequires:      blender
Requires:           blender, thebounty == %{version}

%description
TheBounty is a free montecarlo raytracing engine. This blender plugin provides first class support for Blender.

Raytracing is a rendering technique for generating realistic images by tracing the path of light through a 3D scene. A render engine consists of a specialised computer program that interacts with a host 3D application to provide specific raytracing capabilities "on demand".

The TheBounty engine is supported in Blender and Wings 3D.

%prep
ls
%autosetup -n %{name}-%{version}

%build

%install
%define blenderversion %(rpm -qa --queryformat '%%{version}' blender)
%define plugindir %{_datadir}/blender/%{blenderversion}/scripts/addons/thebounty/
sed -i -e 's@^PLUGIN_PATH.*$@PLUGIN_PATH = "%{_libdir}/thebounty/"@' __init__.py
install -d %{buildroot}%{plugindir}
cp -r . %{buildroot}%{plugindir}

%files
%doc README
%{plugindir}/*

%changelog
* Sun Aug 28 2016 Ruben De Smet <ruben.de.smet@thebountyrenderer.org> 0.1.6.rc4-1
- First automatic build

