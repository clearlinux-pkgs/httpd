%define pprefix /usr/bin
%define plibdir /usr/lib
%define pcontentdir /usr/share/httpd
%define psysconfdir /usr/share/defaults/httpd
%define pincludedir /usr/include/httpd
%define pmandir /usr/share/man
%define suexec_caller apache
%define mpms worker prefork
Name     : httpd
Version  : 2.4.18
Release  : 62
URL      : http://download.nextag.com/apache//httpd/httpd-2.4.18.tar.gz
Source0  : http://download.nextag.com/apache//httpd/httpd-2.4.18.tar.gz
Source1  : httpd.service
Source2  : httpd.tmpfiles
Summary  : Apache HTTP Server
Group    : Development/Tools
License  : Apache-2.0
Requires: httpd-bin
Requires: httpd-lib
Requires: httpd-config
Requires: httpd-data
Requires: httpd-doc
BuildRequires : apr-dev
BuildRequires : apr-util-dev
BuildRequires : cmake
BuildRequires : expat-dev
BuildRequires : openssl-dev
BuildRequires : pcre
BuildRequires : pcre-dev
BuildRequires : util-linux-dev
Patch1: 0001-default-config.patch
Patch2: 0002-do-not-crash-when-IncludeOptional-dir-is-not-existent.patch
Patch3: 0003-Look-fo-envvars-in-etc-httpd.patch

%description
Apache is a powerful, full-featured, efficient, and freely-available
Web server. Apache is also the most popular Web server on the
Internet.

%package bin
Summary: bin components for the httpd package.
Group: Binaries
Requires: httpd-data
Requires: httpd-config

%description bin
bin components for the httpd package.


%package config
Summary: config components for the httpd package.
Group: Default

%description config
config components for the httpd package.


%package data
Summary: data components for the httpd package.
Group: Data

%description data
data components for the httpd package.


%package dev
Summary: dev components for the httpd package.
Group: Development/Libraries
Requires: httpd-lib
Requires: httpd-bin
Requires: httpd-data
Provides: httpd-devel

%description dev
dev components for the httpd package.

%package doc
Summary: doc components for the httpd package.
Group: Documentation

%description doc
doc components for the httpd package.

%package lib
Summary: lib components for the httpd package.
Group: Libraries
Requires: httpd-data
Requires: httpd-config

%description lib
lib components for the httpd package.


%prep
%setup -q -n httpd-2.4.18
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
# forcibly prevent use of bundled apr, apr-util, pcre
rm -rf srclib/{apr,apr-util,pcre}

# regenerate configure scripts
autoheader && autoconf || exit 1

function mpmbuild()
{
mpm=$1; shift
mkdir $mpm; pushd $mpm
../configure \
	--prefix=%{pprefix} \
	--bindir=%{pprefix} \
	--sbindir=%{pprefix} \
	--libdir=%{plibdir} \
	--sysconfdir=%{psysconfdir} \
	--includedir=%{pincludedir} \
	--libexecdir=%{plibdir}/httpd/modules \
	--datadir=%{pcontentdir} \
	--mandir=%{pmandir} \
	--with-installbuilddir=%{plibdir}/httpd/build \
	--with-mpm=$mpm \
	--with-apr=%{pprefix}/apr-1-config --with-apr-util=%{pprefix} \
	--enable-suexec --with-suexec \
	--with-suexec-caller=%{suexec_caller} \
	--enable-fcgid \
	--with-suexec-docroot=%{contentdir} \
	--with-suexec-logfile=%{_localstatedir}/log/httpd/suexec.log \
	--with-suexec-bin=%{_sbindir}/suexec \
	--with-suexec-uidmin=500 --with-suexec-gidmin=100 \
	--enable-pie \
	--enable-mods-shared=all \
	--with-pcre \
	$*

make V=1 %{?_smp_mflags}
popd
}

# Build everything and the kitchen sink with the prefork build
mpmbuild prefork \
	--enable-ssl \
	--with-ssl \
	--enable-distcache \
	--enable-proxy \
	--enable-cache \
	--enable-disk-cache \
	--enable-authn-anon --enable-authn-alias \
	--disable-imagemap

# For the other MPMs, just build httpd and no optional modules
mpmbuild worker
mpmbuild event

%install
rm -rf $RPM_BUILD_ROOT

pushd event
make DESTDIR=%{buildroot} install
popd

# install alternative MPMs
for f in %{mpms}; do
	install -m 755 ${f}/httpd %{buildroot}%{pprefix}/httpd.${f}
done

mkdir -p %{buildroot}/usr/lib/systemd/system
install -m 0644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/httpd.service
mkdir -p %{buildroot}/usr/lib/tmpfiles.d
install -m 0644 %{SOURCE2} %{buildroot}/usr/lib/tmpfiles.d/httpd.conf

%files
%defattr(-,root,root,-)
%{plibdir}/httpd/modules/httpd.exp

%files bin
%defattr(-,root,root,-)
%{pprefix}/*

%files config
%defattr(-,root,root,-)
%{plibdir}/systemd/system/httpd.service
%{plibdir}/tmpfiles.d/httpd.conf

%files data
%defattr(-,root,root,-)
%{psysconfdir}/*
%{pcontentdir}/*

%files dev
%defattr(-,root,root,-)
%{pincludedir}/*.h

%files doc
%defattr(-,root,root,-)
%doc %{pmandir}/man1/*
%doc %{pmandir}/man8/*

%files lib
%defattr(-,root,root,-)
%{plibdir}/httpd/modules/mod*.so
