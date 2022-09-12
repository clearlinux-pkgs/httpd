%define mpms worker prefork
Name     : httpd
Version  : 2.4.54
Release  : 108
URL      : https://mirrors.ocf.berkeley.edu/apache/httpd/httpd-2.4.54.tar.bz2
Source0  : https://mirrors.ocf.berkeley.edu/apache/httpd/httpd-2.4.54.tar.bz2
Source1  : httpd.service
Source2  : httpd.tmpfiles
Source3  : systemd.conf
Source4  : webroot-setup.service
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
BuildRequires : zlib-dev
BuildRequires : nghttp2-dev
BuildRequires : systemd-dev
BuildRequires : curl-dev

Patch1: 0001-default-config.patch
Patch2: 0002-Look-for-envvars-in-etc-httpd.patch
Patch3: 0003-pgo-feature-update.patch
Patch4: 0004-reduce-wakeups.patch
Patch5: 0005-Move-var-www-htdocs-to-var-www-html-to-unify-with-ng.patch

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

%package extras
Summary: extra components for the httpd package.
Group: Data

%description extras
extra components for the httpd package.


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
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
export http_proxy=http://127.0.0.1:9/
export https_proxy=http://127.0.0.1:9/
export no_proxy=localhost,127.0.0.1,0.0.0.0
export LANG=C.UTF-8
export GCC_IGNORE_WERROR=1
export AR=gcc-ar
export NM=gcc-nm
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS  -ffat-lto-objects -flto=16 -ffunction-sections -fno-semantic-interposition -O3 -falign-functions=16 -falign-loops=16"
export CXXFLAGS="$CXXFLAGS  -ffat-lto-objects -flto=16 -ffunction-sections -fno-semantic-interposition -O3 "

# build a temporal httpd with pgo generation enabled
mkdir tmp; pushd tmp
../configure \
	--prefix=%{buildroot}/usr \
	--with-mpm=event \
	--enable-mods-shared=all \
	--enable-fcgid \
	--enable-pie \
	--enable-http2 \
	--enable-systemd \
	--with-pcre=yes \
	--with-port=8088 \
	--with-apr=/usr/bin/apr-1-config --with-apr-util=/usr/bin

make enable-pgo-flags V=1 %{?_smp_mflags}
make DESTDIR=%{buildroot} install
ln -s %{buildroot}%{buildroot}/usr %{buildroot}/usr
make DESTDIR=%{buildroot} pgo-generate
popd

rm -rf %{buildroot}%{buildroot}
rm -rf %{buildroot}/usr
rm -rf tmp

# forcibly prevent use of bundled apr, apr-util, pcre
rm -rf srclib/{apr,apr-util,pcre}

# regenerate configure scripts
autoheader && autoconf || exit 1

export AR=gcc-ar
export RANLIB=gcc-ranlib
export CFLAGS="$CFLAGS -ffat-lto-objects -flto -ffunction-sections -fno-semantic-interposition -O3 -falign-functions=16 -falign-loops=16"
export CXXFLAGS="$CXXFLAGS -ffat-lto-objects -flto -ffunction-sections -fno-semantic-interposition -O3 "

#configure and make using pgo profiles generated previously
function mpmbuild()
{
mpm=$1; shift
mkdir $mpm; pushd $mpm
../configure \
	--prefix=/usr \
	--sysconfdir=/usr/share/defaults/httpd \
	--mandir=/usr/share/man \
	--datadir=/var/www \
	--includedir=/usr/include/httpd \
	--libdir=/usr/lib \
	--libexecdir=/usr/lib/httpd/modules \
	--with-apr=/usr/bin/apr-1-config --with-apr-util=/usr/bin \
	--with-mpm=$mpm \
	--enable-so \
	--enable-systemd \
	--enable-fcgid \
	--enable-http2 \
	--enable-mods-shared="all authz_core auth_basic access_compat alias autoindex dir env filter headers mime reqtimeout status setenvif unixd pie fcgi http2" \
	--with-pcre=yes \
	$* \
	ENABLED_DSO_MODULES="http2"
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
	--enable-http2 \
	--enable-systemd \
	--enable-authn-anon --enable-authn-alias \
	--disable-imagemap

# For the other MPMs, just build httpd and no optional modules
mpmbuild event
mpmbuild worker

%install
rm -rf ${buildroot}

pushd event
make DESTDIR=%{buildroot} install
popd

# install alternative MPMs
for f in %{mpms}; do
	install -m 755 ${f}/httpd %{buildroot}/usr/bin/httpd.${f}
done

mkdir -p %{buildroot}/usr/lib/systemd/system
install -m 0644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/httpd.service
install -m 0644 %{SOURCE4} %{buildroot}/usr/lib/systemd/system/webroot-setup.service
mkdir -p %{buildroot}/usr/lib/tmpfiles.d
install -m 0644 %{SOURCE2} %{buildroot}/usr/lib/tmpfiles.d/httpd.conf
mkdir -p %{buildroot}/usr/share/defaults/httpd/conf.modules.d
install -m 0644 %{SOURCE3} %{buildroot}/usr/share/defaults/httpd/conf.modules.d/systemd.conf
mkdir -p %{buildroot}/usr/share/clr-service-restart
ln -sf /usr/lib/systemd/system/httpd.service %{buildroot}/usr/share/clr-service-restart/httpd.service

# move webroot stuff out of /var, we'll set it up with webroot-setup.service
mv %{buildroot}/var/www %{buildroot}/usr/share/httpd


%files
%defattr(-,root,root,-)
/usr/lib/httpd/modules/httpd.exp

%files bin
%defattr(-,root,root,-)
%exclude /usr/bin/envvars
%exclude /usr/bin/envvars-std
/usr/bin/*
%exclude /usr/bin/apxs
%exclude /usr/bin/dbmmanage

%files extras
%defattr(-,root,root,-)
/usr/bin/apxs
/usr/bin/dbmmanage

%files config
%defattr(-,root,root,-)
/usr/lib/systemd/system/httpd.service
/usr/lib/tmpfiles.d/httpd.conf

%files data
%defattr(-,root,root,-)
%exclude /usr/share/defaults/httpd/original
%exclude /usr/share/defaults/httpd/original/httpd.conf
%exclude /usr/share/defaults/httpd/original/extra
%exclude /usr/share/defaults/httpd/original/extra/*
/usr/share/clr-service-restart/httpd.service
/usr/share/defaults/httpd/*
/usr/share/httpd/*
/usr/lib/systemd/system/webroot-setup.service

%files dev
%defattr(-,root,root,-)
/usr/include/httpd/*.h

%files doc
%defattr(-,root,root,-)
%doc /usr/share/man/man1/*
%doc /usr/share/man/man8/*

%files lib
%defattr(-,root,root,-)
/usr/lib/httpd/modules/mod*.so
