%define mpms worker prefork
Name     : httpd
Version  : 2.4.18
Release  : 66
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
Patch4: 0004-pgo-task.patch
Patch5: wakeups.patch

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
%patch4 -p1
%patch5 -p1

export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 -falign-functions=32 -falign-loops=32"
export CXXFLAGS="$CXXFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 "

# build a temporal httpd with pgo generation enabled
mkdir tmp; pushd tmp
../configure \
	--prefix=%{buildroot}%{_prefix} \
	--with-mpm=event \
	--enable-mods-shared=all \
	--enable-fcgid \
	--enable-pie \
	--with-pcre=yes \
	--with-port=8088 \
	--with-apr=%{_prefix}/bin/apr-1-config --with-apr-util=%{_prefix}/bin

make enable-pgo-flags V=1 %{?_smp_mflags}
make DESTDIR=%{buildroot} install
ln -s %{buildroot}%{buildroot}%{_prefix} %{buildroot}%{_prefix}
make DESTDIR=%{buildroot} pgo-generate
popd

rm -rf %{buildroot}%{buildroot}
rm -rf %{buildroot}%{_prefix}
rm -rf tmp

%build
# forcibly prevent use of bundled apr, apr-util, pcre
rm -rf srclib/{apr,apr-util,pcre}

# regenerate configure scripts
autoheader && autoconf || exit 1

export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 -falign-functions=32 -falign-loops=32"
export CXXFLAGS="$CXXFLAGS -flto -ffunction-sections -fno-semantic-interposition -O3 "

#configure and make using pgo profiles generated previously
function mpmbuild()
{
mpm=$1; shift
mkdir $mpm; pushd $mpm
../configure \
	--prefix=%{_prefix} \
	--sysconfdir=/usr/share/defaults/httpd \
	--mandir=%{_mandir} \
	--datadir=%{_datadir}/httpd \
	--includedir=%{_includedir}/httpd \
	--libdir=%{_prefix}/lib \
	--libexecdir=%{_prefix}/lib/httpd/modules \
	--with-apr=%{_prefix}/bin/apr-1-config --with-apr-util=%{_prefix}/bin \
	--with-mpm=$mpm \
	--enable-fcgid \
	--enable-mods-shared="all authz_core auth_basic access_compat alias autoindex dir env filter headers mime reqtimeout status setenvif unixd pie fcgi" \
	--with-pcre=yes \
	$*
make pgo-use-profile V=1 %{?_smp_mflags}
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
mpmbuild event
mpmbuild worker

%install
rm -rf $RPM_BUILD_ROOT

pushd event
make DESTDIR=%{buildroot} install
popd

# install alternative MPMs
for f in %{mpms}; do
	install -m 755 ${f}/httpd %{buildroot}%{_bindir}/httpd.${f}
done

mkdir -p %{buildroot}/usr/lib/systemd/system
install -m 0644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/httpd.service
mkdir -p %{buildroot}/usr/lib/tmpfiles.d
install -m 0644 %{SOURCE2} %{buildroot}/usr/lib/tmpfiles.d/httpd.conf

%files
%defattr(-,root,root,-)
%{_prefix}/lib/httpd/modules/httpd.exp

%files bin
%defattr(-,root,root,-)
%exclude /usr/bin/envvars
%exclude /usr/bin/envvars-std
/usr/bin/*

%files config
%defattr(-,root,root,-)
%{_prefix}/lib/systemd/system/httpd.service
%{_prefix}/lib/tmpfiles.d/httpd.conf

%files data
%defattr(-,root,root,-)
/usr/share/defaults/httpd/*
/usr/share/httpd/*

%files dev
%defattr(-,root,root,-)
%{_prefix}/include/httpd/*.h

%files doc
%defattr(-,root,root,-)
%doc /usr/share/man/man1/*
%doc /usr/share/man/man8/*

%files lib
%defattr(-,root,root,-)
%{_prefix}/lib/httpd/modules/mod*.so
