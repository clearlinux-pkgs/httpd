%define pprefix /usr/bin
%define plibdir /usr/lib
%define pcontentdir /usr/share/httpd
%define psysconfdir /usr/share/defaults/httpd
%define pincludedir /usr/include/httpd
%define pmandir /usr/share/man
%define suexec_caller apache
%define mpms worker event
Name     : httpd
Version  : 2.4.18
Release  : 51
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
	--with-suexec-docroot=%{contentdir} \
	--with-suexec-logfile=%{_localstatedir}/log/httpd/suexec.log \
	--with-suexec-bin=%{_sbindir}/suexec \
	--with-suexec-uidmin=500 --with-suexec-gidmin=100 \
	--enable-pie \
	--with-pcre \
	$*

make V=1 %{?_smp_mflags}
popd
}

# Build everything and the kitchen sink with the prefork build
mpmbuild prefork \
	--enable-ssl \
	--enable-mods-shared=all \
	--with-ssl \
	--enable-distcache \
	--enable-proxy \
	--enable-cache \
	--enable-disk-cache \
	--enable-cgid \
	--enable-authn-anon --enable-authn-alias \
	--disable-imagemap

# For the other MPMs, just build httpd and no optional modules
for f in %{mpms}; do
	mpmbuild $f --enable-modules=none
done

%install
rm -rf $RPM_BUILD_ROOT

pushd prefork
make DESTDIR=$RPM_BUILD_ROOT install
popd

# install alternative MPMs
for f in %{mpms}; do
	install -m 755 ${f}/httpd %{buildroot}%{pprefix}/httpd.${f}
done

install -m 755 event/httpd %{buildroot}%{pprefix}/httpd


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
/usr/share/defaults/httpd/extra/httpd-autoindex.conf
/usr/share/defaults/httpd/extra/httpd-dav.conf
/usr/share/defaults/httpd/extra/httpd-default.conf
/usr/share/defaults/httpd/extra/httpd-info.conf
/usr/share/defaults/httpd/extra/httpd-languages.conf
/usr/share/defaults/httpd/extra/httpd-manual.conf
/usr/share/defaults/httpd/extra/httpd-mpm.conf
/usr/share/defaults/httpd/extra/httpd-multilang-errordoc.conf
/usr/share/defaults/httpd/extra/httpd-ssl.conf
/usr/share/defaults/httpd/extra/httpd-userdir.conf
/usr/share/defaults/httpd/extra/httpd-vhosts.conf
/usr/share/defaults/httpd/extra/proxy-html.conf
/usr/share/defaults/httpd/httpd.conf
/usr/share/defaults/httpd/magic
/usr/share/defaults/httpd/mime.types
/usr/share/defaults/httpd/original/extra/httpd-autoindex.conf
/usr/share/defaults/httpd/original/extra/httpd-dav.conf
/usr/share/defaults/httpd/original/extra/httpd-default.conf
/usr/share/defaults/httpd/original/extra/httpd-info.conf
/usr/share/defaults/httpd/original/extra/httpd-languages.conf
/usr/share/defaults/httpd/original/extra/httpd-manual.conf
/usr/share/defaults/httpd/original/extra/httpd-mpm.conf
/usr/share/defaults/httpd/original/extra/httpd-multilang-errordoc.conf
/usr/share/defaults/httpd/original/extra/httpd-ssl.conf
/usr/share/defaults/httpd/original/extra/httpd-userdir.conf
/usr/share/defaults/httpd/original/extra/httpd-vhosts.conf
/usr/share/defaults/httpd/original/extra/proxy-html.conf
/usr/share/defaults/httpd/original/httpd.conf
/usr/share/httpd/build/config.nice
/usr/share/httpd/build/config_vars.mk
/usr/share/httpd/build/instdso.sh
/usr/share/httpd/build/library.mk
/usr/share/httpd/build/ltlib.mk
/usr/share/httpd/build/mkdir.sh
/usr/share/httpd/build/program.mk
/usr/share/httpd/build/rules.mk
/usr/share/httpd/build/special.mk
/usr/share/httpd/cgi-bin/printenv
/usr/share/httpd/cgi-bin/printenv.vbs
/usr/share/httpd/cgi-bin/printenv.wsf
/usr/share/httpd/cgi-bin/test-cgi
/usr/share/httpd/error/HTTP_BAD_GATEWAY.html.var
/usr/share/httpd/error/HTTP_BAD_REQUEST.html.var
/usr/share/httpd/error/HTTP_FORBIDDEN.html.var
/usr/share/httpd/error/HTTP_GONE.html.var
/usr/share/httpd/error/HTTP_INTERNAL_SERVER_ERROR.html.var
/usr/share/httpd/error/HTTP_LENGTH_REQUIRED.html.var
/usr/share/httpd/error/HTTP_METHOD_NOT_ALLOWED.html.var
/usr/share/httpd/error/HTTP_NOT_FOUND.html.var
/usr/share/httpd/error/HTTP_NOT_IMPLEMENTED.html.var
/usr/share/httpd/error/HTTP_PRECONDITION_FAILED.html.var
/usr/share/httpd/error/HTTP_REQUEST_ENTITY_TOO_LARGE.html.var
/usr/share/httpd/error/HTTP_REQUEST_TIME_OUT.html.var
/usr/share/httpd/error/HTTP_REQUEST_URI_TOO_LARGE.html.var
/usr/share/httpd/error/HTTP_SERVICE_UNAVAILABLE.html.var
/usr/share/httpd/error/HTTP_UNAUTHORIZED.html.var
/usr/share/httpd/error/HTTP_UNSUPPORTED_MEDIA_TYPE.html.var
/usr/share/httpd/error/HTTP_VARIANT_ALSO_VARIES.html.var
/usr/share/httpd/error/README
/usr/share/httpd/error/contact.html.var
/usr/share/httpd/error/include/bottom.html
/usr/share/httpd/error/include/spacer.html
/usr/share/httpd/error/include/top.html
/usr/share/httpd/htdocs/index.html
/usr/share/httpd/icons/README
/usr/share/httpd/icons/README.html
/usr/share/httpd/icons/a.gif
/usr/share/httpd/icons/a.png
/usr/share/httpd/icons/alert.black.gif
/usr/share/httpd/icons/alert.black.png
/usr/share/httpd/icons/alert.red.gif
/usr/share/httpd/icons/alert.red.png
/usr/share/httpd/icons/apache_pb.gif
/usr/share/httpd/icons/apache_pb.png
/usr/share/httpd/icons/apache_pb.svg
/usr/share/httpd/icons/apache_pb2.gif
/usr/share/httpd/icons/apache_pb2.png
/usr/share/httpd/icons/back.gif
/usr/share/httpd/icons/back.png
/usr/share/httpd/icons/ball.gray.gif
/usr/share/httpd/icons/ball.gray.png
/usr/share/httpd/icons/ball.red.gif
/usr/share/httpd/icons/ball.red.png
/usr/share/httpd/icons/binary.gif
/usr/share/httpd/icons/binary.png
/usr/share/httpd/icons/binhex.gif
/usr/share/httpd/icons/binhex.png
/usr/share/httpd/icons/blank.gif
/usr/share/httpd/icons/blank.png
/usr/share/httpd/icons/bomb.gif
/usr/share/httpd/icons/bomb.png
/usr/share/httpd/icons/box1.gif
/usr/share/httpd/icons/box1.png
/usr/share/httpd/icons/box2.gif
/usr/share/httpd/icons/box2.png
/usr/share/httpd/icons/broken.gif
/usr/share/httpd/icons/broken.png
/usr/share/httpd/icons/burst.gif
/usr/share/httpd/icons/burst.png
/usr/share/httpd/icons/c.gif
/usr/share/httpd/icons/c.png
/usr/share/httpd/icons/comp.blue.gif
/usr/share/httpd/icons/comp.blue.png
/usr/share/httpd/icons/comp.gray.gif
/usr/share/httpd/icons/comp.gray.png
/usr/share/httpd/icons/compressed.gif
/usr/share/httpd/icons/compressed.png
/usr/share/httpd/icons/continued.gif
/usr/share/httpd/icons/continued.png
/usr/share/httpd/icons/dir.gif
/usr/share/httpd/icons/dir.png
/usr/share/httpd/icons/diskimg.gif
/usr/share/httpd/icons/diskimg.png
/usr/share/httpd/icons/down.gif
/usr/share/httpd/icons/down.png
/usr/share/httpd/icons/dvi.gif
/usr/share/httpd/icons/dvi.png
/usr/share/httpd/icons/f.gif
/usr/share/httpd/icons/f.png
/usr/share/httpd/icons/folder.gif
/usr/share/httpd/icons/folder.open.gif
/usr/share/httpd/icons/folder.open.png
/usr/share/httpd/icons/folder.png
/usr/share/httpd/icons/folder.sec.gif
/usr/share/httpd/icons/folder.sec.png
/usr/share/httpd/icons/forward.gif
/usr/share/httpd/icons/forward.png
/usr/share/httpd/icons/generic.gif
/usr/share/httpd/icons/generic.png
/usr/share/httpd/icons/generic.red.gif
/usr/share/httpd/icons/generic.red.png
/usr/share/httpd/icons/generic.sec.gif
/usr/share/httpd/icons/generic.sec.png
/usr/share/httpd/icons/hand.right.gif
/usr/share/httpd/icons/hand.right.png
/usr/share/httpd/icons/hand.up.gif
/usr/share/httpd/icons/hand.up.png
/usr/share/httpd/icons/icon.sheet.gif
/usr/share/httpd/icons/icon.sheet.png
/usr/share/httpd/icons/image1.gif
/usr/share/httpd/icons/image1.png
/usr/share/httpd/icons/image2.gif
/usr/share/httpd/icons/image2.png
/usr/share/httpd/icons/image3.gif
/usr/share/httpd/icons/image3.png
/usr/share/httpd/icons/index.gif
/usr/share/httpd/icons/index.png
/usr/share/httpd/icons/layout.gif
/usr/share/httpd/icons/layout.png
/usr/share/httpd/icons/left.gif
/usr/share/httpd/icons/left.png
/usr/share/httpd/icons/link.gif
/usr/share/httpd/icons/link.png
/usr/share/httpd/icons/movie.gif
/usr/share/httpd/icons/movie.png
/usr/share/httpd/icons/odf6odb.png
/usr/share/httpd/icons/odf6odc.png
/usr/share/httpd/icons/odf6odf.png
/usr/share/httpd/icons/odf6odg.png
/usr/share/httpd/icons/odf6odi.png
/usr/share/httpd/icons/odf6odm.png
/usr/share/httpd/icons/odf6odp.png
/usr/share/httpd/icons/odf6ods.png
/usr/share/httpd/icons/odf6odt.png
/usr/share/httpd/icons/odf6otc.png
/usr/share/httpd/icons/odf6otf.png
/usr/share/httpd/icons/odf6otg.png
/usr/share/httpd/icons/odf6oth.png
/usr/share/httpd/icons/odf6oti.png
/usr/share/httpd/icons/odf6otp.png
/usr/share/httpd/icons/odf6ots.png
/usr/share/httpd/icons/odf6ott.png
/usr/share/httpd/icons/p.gif
/usr/share/httpd/icons/p.png
/usr/share/httpd/icons/patch.gif
/usr/share/httpd/icons/patch.png
/usr/share/httpd/icons/pdf.gif
/usr/share/httpd/icons/pdf.png
/usr/share/httpd/icons/pie0.gif
/usr/share/httpd/icons/pie0.png
/usr/share/httpd/icons/pie1.gif
/usr/share/httpd/icons/pie1.png
/usr/share/httpd/icons/pie2.gif
/usr/share/httpd/icons/pie2.png
/usr/share/httpd/icons/pie3.gif
/usr/share/httpd/icons/pie3.png
/usr/share/httpd/icons/pie4.gif
/usr/share/httpd/icons/pie4.png
/usr/share/httpd/icons/pie5.gif
/usr/share/httpd/icons/pie5.png
/usr/share/httpd/icons/pie6.gif
/usr/share/httpd/icons/pie6.png
/usr/share/httpd/icons/pie7.gif
/usr/share/httpd/icons/pie7.png
/usr/share/httpd/icons/pie8.gif
/usr/share/httpd/icons/pie8.png
/usr/share/httpd/icons/portal.gif
/usr/share/httpd/icons/portal.png
/usr/share/httpd/icons/ps.gif
/usr/share/httpd/icons/ps.png
/usr/share/httpd/icons/quill.gif
/usr/share/httpd/icons/quill.png
/usr/share/httpd/icons/right.gif
/usr/share/httpd/icons/right.png
/usr/share/httpd/icons/screw1.gif
/usr/share/httpd/icons/screw1.png
/usr/share/httpd/icons/screw2.gif
/usr/share/httpd/icons/screw2.png
/usr/share/httpd/icons/script.gif
/usr/share/httpd/icons/script.png
/usr/share/httpd/icons/small/back.gif
/usr/share/httpd/icons/small/back.png
/usr/share/httpd/icons/small/binary.gif
/usr/share/httpd/icons/small/binary.png
/usr/share/httpd/icons/small/binhex.gif
/usr/share/httpd/icons/small/binhex.png
/usr/share/httpd/icons/small/blank.gif
/usr/share/httpd/icons/small/blank.png
/usr/share/httpd/icons/small/broken.gif
/usr/share/httpd/icons/small/broken.png
/usr/share/httpd/icons/small/burst.gif
/usr/share/httpd/icons/small/burst.png
/usr/share/httpd/icons/small/comp1.gif
/usr/share/httpd/icons/small/comp1.png
/usr/share/httpd/icons/small/comp2.gif
/usr/share/httpd/icons/small/comp2.png
/usr/share/httpd/icons/small/compressed.gif
/usr/share/httpd/icons/small/compressed.png
/usr/share/httpd/icons/small/continued.gif
/usr/share/httpd/icons/small/continued.png
/usr/share/httpd/icons/small/doc.gif
/usr/share/httpd/icons/small/doc.png
/usr/share/httpd/icons/small/folder.gif
/usr/share/httpd/icons/small/folder.png
/usr/share/httpd/icons/small/folder2.gif
/usr/share/httpd/icons/small/folder2.png
/usr/share/httpd/icons/small/forward.gif
/usr/share/httpd/icons/small/forward.png
/usr/share/httpd/icons/small/generic.gif
/usr/share/httpd/icons/small/generic.png
/usr/share/httpd/icons/small/generic2.gif
/usr/share/httpd/icons/small/generic2.png
/usr/share/httpd/icons/small/generic3.gif
/usr/share/httpd/icons/small/generic3.png
/usr/share/httpd/icons/small/image.gif
/usr/share/httpd/icons/small/image.png
/usr/share/httpd/icons/small/image2.gif
/usr/share/httpd/icons/small/image2.png
/usr/share/httpd/icons/small/index.gif
/usr/share/httpd/icons/small/index.png
/usr/share/httpd/icons/small/key.gif
/usr/share/httpd/icons/small/key.png
/usr/share/httpd/icons/small/movie.gif
/usr/share/httpd/icons/small/movie.png
/usr/share/httpd/icons/small/patch.gif
/usr/share/httpd/icons/small/patch.png
/usr/share/httpd/icons/small/ps.gif
/usr/share/httpd/icons/small/ps.png
/usr/share/httpd/icons/small/rainbow.gif
/usr/share/httpd/icons/small/rainbow.png
/usr/share/httpd/icons/small/sound.gif
/usr/share/httpd/icons/small/sound.png
/usr/share/httpd/icons/small/sound2.gif
/usr/share/httpd/icons/small/sound2.png
/usr/share/httpd/icons/small/tar.gif
/usr/share/httpd/icons/small/tar.png
/usr/share/httpd/icons/small/text.gif
/usr/share/httpd/icons/small/text.png
/usr/share/httpd/icons/small/transfer.gif
/usr/share/httpd/icons/small/transfer.png
/usr/share/httpd/icons/small/unknown.gif
/usr/share/httpd/icons/small/unknown.png
/usr/share/httpd/icons/small/uu.gif
/usr/share/httpd/icons/small/uu.png
/usr/share/httpd/icons/sound1.gif
/usr/share/httpd/icons/sound1.png
/usr/share/httpd/icons/sound2.gif
/usr/share/httpd/icons/sound2.png
/usr/share/httpd/icons/sphere1.gif
/usr/share/httpd/icons/sphere1.png
/usr/share/httpd/icons/sphere2.gif
/usr/share/httpd/icons/sphere2.png
/usr/share/httpd/icons/svg.png
/usr/share/httpd/icons/tar.gif
/usr/share/httpd/icons/tar.png
/usr/share/httpd/icons/tex.gif
/usr/share/httpd/icons/tex.png
/usr/share/httpd/icons/text.gif
/usr/share/httpd/icons/text.png
/usr/share/httpd/icons/transfer.gif
/usr/share/httpd/icons/transfer.png
/usr/share/httpd/icons/unknown.gif
/usr/share/httpd/icons/unknown.png
/usr/share/httpd/icons/up.gif
/usr/share/httpd/icons/up.png
/usr/share/httpd/icons/uu.gif
/usr/share/httpd/icons/uu.png
/usr/share/httpd/icons/uuencoded.gif
/usr/share/httpd/icons/uuencoded.png
/usr/share/httpd/icons/world1.gif
/usr/share/httpd/icons/world1.png
/usr/share/httpd/icons/world2.gif
/usr/share/httpd/icons/world2.png
/usr/share/httpd/icons/xml.png
/usr/share/httpd/manual/BUILDING
/usr/share/httpd/manual/LICENSE
/usr/share/httpd/manual/bind.html
/usr/share/httpd/manual/bind.html.de
/usr/share/httpd/manual/bind.html.en
/usr/share/httpd/manual/bind.html.fr
/usr/share/httpd/manual/bind.html.ja.utf8
/usr/share/httpd/manual/bind.html.ko.euc-kr
/usr/share/httpd/manual/bind.html.tr.utf8
/usr/share/httpd/manual/caching.html
/usr/share/httpd/manual/caching.html.en
/usr/share/httpd/manual/caching.html.fr
/usr/share/httpd/manual/caching.html.tr.utf8
/usr/share/httpd/manual/configuring.html
/usr/share/httpd/manual/configuring.html.de
/usr/share/httpd/manual/configuring.html.en
/usr/share/httpd/manual/configuring.html.fr
/usr/share/httpd/manual/configuring.html.ja.utf8
/usr/share/httpd/manual/configuring.html.ko.euc-kr
/usr/share/httpd/manual/configuring.html.tr.utf8
/usr/share/httpd/manual/content-negotiation.html
/usr/share/httpd/manual/content-negotiation.html.en
/usr/share/httpd/manual/content-negotiation.html.fr
/usr/share/httpd/manual/content-negotiation.html.ja.utf8
/usr/share/httpd/manual/content-negotiation.html.ko.euc-kr
/usr/share/httpd/manual/content-negotiation.html.tr.utf8
/usr/share/httpd/manual/convenience.map
/usr/share/httpd/manual/custom-error.html
/usr/share/httpd/manual/custom-error.html.en
/usr/share/httpd/manual/custom-error.html.es
/usr/share/httpd/manual/custom-error.html.fr
/usr/share/httpd/manual/custom-error.html.ja.utf8
/usr/share/httpd/manual/custom-error.html.ko.euc-kr
/usr/share/httpd/manual/custom-error.html.tr.utf8
/usr/share/httpd/manual/developer/API.html
/usr/share/httpd/manual/developer/API.html.en
/usr/share/httpd/manual/developer/debugging.html
/usr/share/httpd/manual/developer/debugging.html.en
/usr/share/httpd/manual/developer/documenting.html
/usr/share/httpd/manual/developer/documenting.html.en
/usr/share/httpd/manual/developer/documenting.html.zh-cn.utf8
/usr/share/httpd/manual/developer/filters.html
/usr/share/httpd/manual/developer/filters.html.en
/usr/share/httpd/manual/developer/hooks.html
/usr/share/httpd/manual/developer/hooks.html.en
/usr/share/httpd/manual/developer/index.html
/usr/share/httpd/manual/developer/index.html.en
/usr/share/httpd/manual/developer/index.html.zh-cn.utf8
/usr/share/httpd/manual/developer/modguide.html
/usr/share/httpd/manual/developer/modguide.html.en
/usr/share/httpd/manual/developer/modules.html
/usr/share/httpd/manual/developer/modules.html.en
/usr/share/httpd/manual/developer/modules.html.ja.utf8
/usr/share/httpd/manual/developer/new_api_2_4.html
/usr/share/httpd/manual/developer/new_api_2_4.html.en
/usr/share/httpd/manual/developer/output-filters.html
/usr/share/httpd/manual/developer/output-filters.html.en
/usr/share/httpd/manual/developer/request.html
/usr/share/httpd/manual/developer/request.html.en
/usr/share/httpd/manual/developer/thread_safety.html
/usr/share/httpd/manual/developer/thread_safety.html.en
/usr/share/httpd/manual/dns-caveats.html
/usr/share/httpd/manual/dns-caveats.html.en
/usr/share/httpd/manual/dns-caveats.html.fr
/usr/share/httpd/manual/dns-caveats.html.ja.utf8
/usr/share/httpd/manual/dns-caveats.html.ko.euc-kr
/usr/share/httpd/manual/dns-caveats.html.tr.utf8
/usr/share/httpd/manual/dso.html
/usr/share/httpd/manual/dso.html.en
/usr/share/httpd/manual/dso.html.fr
/usr/share/httpd/manual/dso.html.ja.utf8
/usr/share/httpd/manual/dso.html.ko.euc-kr
/usr/share/httpd/manual/dso.html.tr.utf8
/usr/share/httpd/manual/env.html
/usr/share/httpd/manual/env.html.en
/usr/share/httpd/manual/env.html.fr
/usr/share/httpd/manual/env.html.ja.utf8
/usr/share/httpd/manual/env.html.ko.euc-kr
/usr/share/httpd/manual/env.html.tr.utf8
/usr/share/httpd/manual/expr.html
/usr/share/httpd/manual/expr.html.en
/usr/share/httpd/manual/expr.html.fr
/usr/share/httpd/manual/faq/index.html
/usr/share/httpd/manual/faq/index.html.en
/usr/share/httpd/manual/faq/index.html.fr
/usr/share/httpd/manual/faq/index.html.tr.utf8
/usr/share/httpd/manual/faq/index.html.zh-cn.utf8
/usr/share/httpd/manual/filter.html
/usr/share/httpd/manual/filter.html.en
/usr/share/httpd/manual/filter.html.es
/usr/share/httpd/manual/filter.html.fr
/usr/share/httpd/manual/filter.html.ja.utf8
/usr/share/httpd/manual/filter.html.ko.euc-kr
/usr/share/httpd/manual/filter.html.tr.utf8
/usr/share/httpd/manual/getting-started.html
/usr/share/httpd/manual/getting-started.html.en
/usr/share/httpd/manual/getting-started.html.fr
/usr/share/httpd/manual/glossary.html
/usr/share/httpd/manual/glossary.html.de
/usr/share/httpd/manual/glossary.html.en
/usr/share/httpd/manual/glossary.html.es
/usr/share/httpd/manual/glossary.html.fr
/usr/share/httpd/manual/glossary.html.ja.utf8
/usr/share/httpd/manual/glossary.html.ko.euc-kr
/usr/share/httpd/manual/glossary.html.tr.utf8
/usr/share/httpd/manual/handler.html
/usr/share/httpd/manual/handler.html.en
/usr/share/httpd/manual/handler.html.es
/usr/share/httpd/manual/handler.html.fr
/usr/share/httpd/manual/handler.html.ja.utf8
/usr/share/httpd/manual/handler.html.ko.euc-kr
/usr/share/httpd/manual/handler.html.tr.utf8
/usr/share/httpd/manual/handler.html.zh-cn.utf8
/usr/share/httpd/manual/howto/access.html
/usr/share/httpd/manual/howto/access.html.en
/usr/share/httpd/manual/howto/access.html.fr
/usr/share/httpd/manual/howto/auth.html
/usr/share/httpd/manual/howto/auth.html.en
/usr/share/httpd/manual/howto/auth.html.fr
/usr/share/httpd/manual/howto/auth.html.ja.utf8
/usr/share/httpd/manual/howto/auth.html.ko.euc-kr
/usr/share/httpd/manual/howto/auth.html.tr.utf8
/usr/share/httpd/manual/howto/cgi.html
/usr/share/httpd/manual/howto/cgi.html.en
/usr/share/httpd/manual/howto/cgi.html.fr
/usr/share/httpd/manual/howto/cgi.html.ja.utf8
/usr/share/httpd/manual/howto/cgi.html.ko.euc-kr
/usr/share/httpd/manual/howto/htaccess.html
/usr/share/httpd/manual/howto/htaccess.html.en
/usr/share/httpd/manual/howto/htaccess.html.fr
/usr/share/httpd/manual/howto/htaccess.html.ja.utf8
/usr/share/httpd/manual/howto/htaccess.html.ko.euc-kr
/usr/share/httpd/manual/howto/htaccess.html.pt-br
/usr/share/httpd/manual/howto/index.html
/usr/share/httpd/manual/howto/index.html.en
/usr/share/httpd/manual/howto/index.html.fr
/usr/share/httpd/manual/howto/index.html.ja.utf8
/usr/share/httpd/manual/howto/index.html.ko.euc-kr
/usr/share/httpd/manual/howto/index.html.zh-cn.utf8
/usr/share/httpd/manual/howto/public_html.html
/usr/share/httpd/manual/howto/public_html.html.en
/usr/share/httpd/manual/howto/public_html.html.fr
/usr/share/httpd/manual/howto/public_html.html.ja.utf8
/usr/share/httpd/manual/howto/public_html.html.ko.euc-kr
/usr/share/httpd/manual/howto/public_html.html.tr.utf8
/usr/share/httpd/manual/howto/ssi.html
/usr/share/httpd/manual/howto/ssi.html.en
/usr/share/httpd/manual/howto/ssi.html.fr
/usr/share/httpd/manual/howto/ssi.html.ja.utf8
/usr/share/httpd/manual/howto/ssi.html.ko.euc-kr
/usr/share/httpd/manual/images/apache_header.gif
/usr/share/httpd/manual/images/build_a_mod_2.png
/usr/share/httpd/manual/images/build_a_mod_3.png
/usr/share/httpd/manual/images/build_a_mod_4.png
/usr/share/httpd/manual/images/caching_fig1.gif
/usr/share/httpd/manual/images/caching_fig1.png
/usr/share/httpd/manual/images/caching_fig1.tr.png
/usr/share/httpd/manual/images/custom_errordocs.png
/usr/share/httpd/manual/images/down.gif
/usr/share/httpd/manual/images/favicon.ico
/usr/share/httpd/manual/images/feather.gif
/usr/share/httpd/manual/images/feather.png
/usr/share/httpd/manual/images/filter_arch.png
/usr/share/httpd/manual/images/filter_arch.tr.png
/usr/share/httpd/manual/images/home.gif
/usr/share/httpd/manual/images/index.gif
/usr/share/httpd/manual/images/left.gif
/usr/share/httpd/manual/images/mod_filter_new.gif
/usr/share/httpd/manual/images/mod_filter_new.png
/usr/share/httpd/manual/images/mod_filter_new.tr.png
/usr/share/httpd/manual/images/mod_filter_old.gif
/usr/share/httpd/manual/images/mod_filter_old.png
/usr/share/httpd/manual/images/mod_rewrite_fig1.gif
/usr/share/httpd/manual/images/mod_rewrite_fig1.png
/usr/share/httpd/manual/images/mod_rewrite_fig2.gif
/usr/share/httpd/manual/images/mod_rewrite_fig2.png
/usr/share/httpd/manual/images/pixel.gif
/usr/share/httpd/manual/images/rewrite_backreferences.png
/usr/share/httpd/manual/images/rewrite_process_uri.png
/usr/share/httpd/manual/images/rewrite_rule_flow.png
/usr/share/httpd/manual/images/right.gif
/usr/share/httpd/manual/images/ssl_intro_fig1.gif
/usr/share/httpd/manual/images/ssl_intro_fig1.png
/usr/share/httpd/manual/images/ssl_intro_fig2.gif
/usr/share/httpd/manual/images/ssl_intro_fig2.png
/usr/share/httpd/manual/images/ssl_intro_fig3.gif
/usr/share/httpd/manual/images/ssl_intro_fig3.png
/usr/share/httpd/manual/images/sub.gif
/usr/share/httpd/manual/images/syntax_rewritecond.png
/usr/share/httpd/manual/images/syntax_rewriterule.png
/usr/share/httpd/manual/images/up.gif
/usr/share/httpd/manual/index.html
/usr/share/httpd/manual/index.html.da
/usr/share/httpd/manual/index.html.de
/usr/share/httpd/manual/index.html.en
/usr/share/httpd/manual/index.html.es
/usr/share/httpd/manual/index.html.fr
/usr/share/httpd/manual/index.html.ja.utf8
/usr/share/httpd/manual/index.html.ko.euc-kr
/usr/share/httpd/manual/index.html.pt-br
/usr/share/httpd/manual/index.html.tr.utf8
/usr/share/httpd/manual/index.html.zh-cn.utf8
/usr/share/httpd/manual/install.html
/usr/share/httpd/manual/install.html.de
/usr/share/httpd/manual/install.html.en
/usr/share/httpd/manual/install.html.es
/usr/share/httpd/manual/install.html.fr
/usr/share/httpd/manual/install.html.ja.utf8
/usr/share/httpd/manual/install.html.ko.euc-kr
/usr/share/httpd/manual/install.html.tr.utf8
/usr/share/httpd/manual/invoking.html
/usr/share/httpd/manual/invoking.html.de
/usr/share/httpd/manual/invoking.html.en
/usr/share/httpd/manual/invoking.html.es
/usr/share/httpd/manual/invoking.html.fr
/usr/share/httpd/manual/invoking.html.ja.utf8
/usr/share/httpd/manual/invoking.html.ko.euc-kr
/usr/share/httpd/manual/invoking.html.tr.utf8
/usr/share/httpd/manual/license.html
/usr/share/httpd/manual/license.html.en
/usr/share/httpd/manual/logs.html
/usr/share/httpd/manual/logs.html.en
/usr/share/httpd/manual/logs.html.fr
/usr/share/httpd/manual/logs.html.ja.utf8
/usr/share/httpd/manual/logs.html.ko.euc-kr
/usr/share/httpd/manual/logs.html.tr.utf8
/usr/share/httpd/manual/misc/index.html
/usr/share/httpd/manual/misc/index.html.en
/usr/share/httpd/manual/misc/index.html.fr
/usr/share/httpd/manual/misc/index.html.ko.euc-kr
/usr/share/httpd/manual/misc/index.html.tr.utf8
/usr/share/httpd/manual/misc/index.html.zh-cn.utf8
/usr/share/httpd/manual/misc/password_encryptions.html
/usr/share/httpd/manual/misc/password_encryptions.html.en
/usr/share/httpd/manual/misc/password_encryptions.html.fr
/usr/share/httpd/manual/misc/perf-tuning.html
/usr/share/httpd/manual/misc/perf-tuning.html.en
/usr/share/httpd/manual/misc/perf-tuning.html.fr
/usr/share/httpd/manual/misc/perf-tuning.html.ko.euc-kr
/usr/share/httpd/manual/misc/perf-tuning.html.tr.utf8
/usr/share/httpd/manual/misc/relevant_standards.html
/usr/share/httpd/manual/misc/relevant_standards.html.en
/usr/share/httpd/manual/misc/relevant_standards.html.fr
/usr/share/httpd/manual/misc/relevant_standards.html.ko.euc-kr
/usr/share/httpd/manual/misc/security_tips.html
/usr/share/httpd/manual/misc/security_tips.html.en
/usr/share/httpd/manual/misc/security_tips.html.fr
/usr/share/httpd/manual/misc/security_tips.html.ko.euc-kr
/usr/share/httpd/manual/misc/security_tips.html.tr.utf8
/usr/share/httpd/manual/mod/core.html
/usr/share/httpd/manual/mod/core.html.de
/usr/share/httpd/manual/mod/core.html.en
/usr/share/httpd/manual/mod/core.html.es
/usr/share/httpd/manual/mod/core.html.fr
/usr/share/httpd/manual/mod/core.html.ja.utf8
/usr/share/httpd/manual/mod/core.html.tr.utf8
/usr/share/httpd/manual/mod/directive-dict.html
/usr/share/httpd/manual/mod/directive-dict.html.en
/usr/share/httpd/manual/mod/directive-dict.html.fr
/usr/share/httpd/manual/mod/directive-dict.html.ja.utf8
/usr/share/httpd/manual/mod/directive-dict.html.ko.euc-kr
/usr/share/httpd/manual/mod/directive-dict.html.tr.utf8
/usr/share/httpd/manual/mod/directives.html
/usr/share/httpd/manual/mod/directives.html.de
/usr/share/httpd/manual/mod/directives.html.en
/usr/share/httpd/manual/mod/directives.html.es
/usr/share/httpd/manual/mod/directives.html.fr
/usr/share/httpd/manual/mod/directives.html.ja.utf8
/usr/share/httpd/manual/mod/directives.html.ko.euc-kr
/usr/share/httpd/manual/mod/directives.html.tr.utf8
/usr/share/httpd/manual/mod/directives.html.zh-cn.utf8
/usr/share/httpd/manual/mod/event.html
/usr/share/httpd/manual/mod/event.html.en
/usr/share/httpd/manual/mod/event.html.fr
/usr/share/httpd/manual/mod/index.html
/usr/share/httpd/manual/mod/index.html.de
/usr/share/httpd/manual/mod/index.html.en
/usr/share/httpd/manual/mod/index.html.es
/usr/share/httpd/manual/mod/index.html.fr
/usr/share/httpd/manual/mod/index.html.ja.utf8
/usr/share/httpd/manual/mod/index.html.ko.euc-kr
/usr/share/httpd/manual/mod/index.html.tr.utf8
/usr/share/httpd/manual/mod/index.html.zh-cn.utf8
/usr/share/httpd/manual/mod/mod_access_compat.html
/usr/share/httpd/manual/mod/mod_access_compat.html.en
/usr/share/httpd/manual/mod/mod_access_compat.html.fr
/usr/share/httpd/manual/mod/mod_access_compat.html.ja.utf8
/usr/share/httpd/manual/mod/mod_actions.html
/usr/share/httpd/manual/mod/mod_actions.html.de
/usr/share/httpd/manual/mod/mod_actions.html.en
/usr/share/httpd/manual/mod/mod_actions.html.fr
/usr/share/httpd/manual/mod/mod_actions.html.ja.utf8
/usr/share/httpd/manual/mod/mod_actions.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_alias.html
/usr/share/httpd/manual/mod/mod_alias.html.en
/usr/share/httpd/manual/mod/mod_alias.html.fr
/usr/share/httpd/manual/mod/mod_alias.html.ja.utf8
/usr/share/httpd/manual/mod/mod_alias.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_alias.html.tr.utf8
/usr/share/httpd/manual/mod/mod_allowmethods.html
/usr/share/httpd/manual/mod/mod_allowmethods.html.en
/usr/share/httpd/manual/mod/mod_allowmethods.html.fr
/usr/share/httpd/manual/mod/mod_asis.html
/usr/share/httpd/manual/mod/mod_asis.html.en
/usr/share/httpd/manual/mod/mod_asis.html.fr
/usr/share/httpd/manual/mod/mod_asis.html.ja.utf8
/usr/share/httpd/manual/mod/mod_asis.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_auth_basic.html
/usr/share/httpd/manual/mod/mod_auth_basic.html.en
/usr/share/httpd/manual/mod/mod_auth_basic.html.fr
/usr/share/httpd/manual/mod/mod_auth_basic.html.ja.utf8
/usr/share/httpd/manual/mod/mod_auth_basic.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_auth_digest.html
/usr/share/httpd/manual/mod/mod_auth_digest.html.en
/usr/share/httpd/manual/mod/mod_auth_digest.html.fr
/usr/share/httpd/manual/mod/mod_auth_digest.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_auth_form.html
/usr/share/httpd/manual/mod/mod_auth_form.html.en
/usr/share/httpd/manual/mod/mod_auth_form.html.fr
/usr/share/httpd/manual/mod/mod_authn_anon.html
/usr/share/httpd/manual/mod/mod_authn_anon.html.en
/usr/share/httpd/manual/mod/mod_authn_anon.html.fr
/usr/share/httpd/manual/mod/mod_authn_anon.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authn_anon.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authn_core.html
/usr/share/httpd/manual/mod/mod_authn_core.html.en
/usr/share/httpd/manual/mod/mod_authn_core.html.fr
/usr/share/httpd/manual/mod/mod_authn_dbd.html
/usr/share/httpd/manual/mod/mod_authn_dbd.html.en
/usr/share/httpd/manual/mod/mod_authn_dbd.html.fr
/usr/share/httpd/manual/mod/mod_authn_dbm.html
/usr/share/httpd/manual/mod/mod_authn_dbm.html.en
/usr/share/httpd/manual/mod/mod_authn_dbm.html.fr
/usr/share/httpd/manual/mod/mod_authn_dbm.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authn_dbm.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authn_file.html
/usr/share/httpd/manual/mod/mod_authn_file.html.en
/usr/share/httpd/manual/mod/mod_authn_file.html.fr
/usr/share/httpd/manual/mod/mod_authn_file.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authn_file.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authn_socache.html
/usr/share/httpd/manual/mod/mod_authn_socache.html.en
/usr/share/httpd/manual/mod/mod_authn_socache.html.fr
/usr/share/httpd/manual/mod/mod_authnz_fcgi.html
/usr/share/httpd/manual/mod/mod_authnz_fcgi.html.en
/usr/share/httpd/manual/mod/mod_authnz_ldap.html
/usr/share/httpd/manual/mod/mod_authnz_ldap.html.en
/usr/share/httpd/manual/mod/mod_authnz_ldap.html.fr
/usr/share/httpd/manual/mod/mod_authz_core.html
/usr/share/httpd/manual/mod/mod_authz_core.html.en
/usr/share/httpd/manual/mod/mod_authz_core.html.fr
/usr/share/httpd/manual/mod/mod_authz_dbd.html
/usr/share/httpd/manual/mod/mod_authz_dbd.html.en
/usr/share/httpd/manual/mod/mod_authz_dbd.html.fr
/usr/share/httpd/manual/mod/mod_authz_dbm.html
/usr/share/httpd/manual/mod/mod_authz_dbm.html.en
/usr/share/httpd/manual/mod/mod_authz_dbm.html.fr
/usr/share/httpd/manual/mod/mod_authz_dbm.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authz_groupfile.html
/usr/share/httpd/manual/mod/mod_authz_groupfile.html.en
/usr/share/httpd/manual/mod/mod_authz_groupfile.html.fr
/usr/share/httpd/manual/mod/mod_authz_groupfile.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authz_groupfile.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authz_host.html
/usr/share/httpd/manual/mod/mod_authz_host.html.en
/usr/share/httpd/manual/mod/mod_authz_host.html.fr
/usr/share/httpd/manual/mod/mod_authz_owner.html
/usr/share/httpd/manual/mod/mod_authz_owner.html.en
/usr/share/httpd/manual/mod/mod_authz_owner.html.fr
/usr/share/httpd/manual/mod/mod_authz_owner.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authz_owner.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_authz_user.html
/usr/share/httpd/manual/mod/mod_authz_user.html.en
/usr/share/httpd/manual/mod/mod_authz_user.html.fr
/usr/share/httpd/manual/mod/mod_authz_user.html.ja.utf8
/usr/share/httpd/manual/mod/mod_authz_user.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_autoindex.html
/usr/share/httpd/manual/mod/mod_autoindex.html.en
/usr/share/httpd/manual/mod/mod_autoindex.html.fr
/usr/share/httpd/manual/mod/mod_autoindex.html.ja.utf8
/usr/share/httpd/manual/mod/mod_autoindex.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_autoindex.html.tr.utf8
/usr/share/httpd/manual/mod/mod_buffer.html
/usr/share/httpd/manual/mod/mod_buffer.html.en
/usr/share/httpd/manual/mod/mod_buffer.html.fr
/usr/share/httpd/manual/mod/mod_cache.html
/usr/share/httpd/manual/mod/mod_cache.html.en
/usr/share/httpd/manual/mod/mod_cache.html.fr
/usr/share/httpd/manual/mod/mod_cache.html.ja.utf8
/usr/share/httpd/manual/mod/mod_cache.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_cache_disk.html
/usr/share/httpd/manual/mod/mod_cache_disk.html.en
/usr/share/httpd/manual/mod/mod_cache_disk.html.fr
/usr/share/httpd/manual/mod/mod_cache_disk.html.ja.utf8
/usr/share/httpd/manual/mod/mod_cache_disk.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_cache_socache.html
/usr/share/httpd/manual/mod/mod_cache_socache.html.en
/usr/share/httpd/manual/mod/mod_cache_socache.html.fr
/usr/share/httpd/manual/mod/mod_cern_meta.html
/usr/share/httpd/manual/mod/mod_cern_meta.html.en
/usr/share/httpd/manual/mod/mod_cern_meta.html.fr
/usr/share/httpd/manual/mod/mod_cern_meta.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_cgi.html
/usr/share/httpd/manual/mod/mod_cgi.html.en
/usr/share/httpd/manual/mod/mod_cgi.html.fr
/usr/share/httpd/manual/mod/mod_cgi.html.ja.utf8
/usr/share/httpd/manual/mod/mod_cgi.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_cgid.html
/usr/share/httpd/manual/mod/mod_cgid.html.en
/usr/share/httpd/manual/mod/mod_cgid.html.fr
/usr/share/httpd/manual/mod/mod_cgid.html.ja.utf8
/usr/share/httpd/manual/mod/mod_cgid.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_charset_lite.html
/usr/share/httpd/manual/mod/mod_charset_lite.html.en
/usr/share/httpd/manual/mod/mod_charset_lite.html.fr
/usr/share/httpd/manual/mod/mod_charset_lite.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_data.html
/usr/share/httpd/manual/mod/mod_data.html.en
/usr/share/httpd/manual/mod/mod_data.html.fr
/usr/share/httpd/manual/mod/mod_dav.html
/usr/share/httpd/manual/mod/mod_dav.html.en
/usr/share/httpd/manual/mod/mod_dav.html.fr
/usr/share/httpd/manual/mod/mod_dav.html.ja.utf8
/usr/share/httpd/manual/mod/mod_dav.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_dav_fs.html
/usr/share/httpd/manual/mod/mod_dav_fs.html.en
/usr/share/httpd/manual/mod/mod_dav_fs.html.fr
/usr/share/httpd/manual/mod/mod_dav_fs.html.ja.utf8
/usr/share/httpd/manual/mod/mod_dav_fs.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_dav_lock.html
/usr/share/httpd/manual/mod/mod_dav_lock.html.en
/usr/share/httpd/manual/mod/mod_dav_lock.html.fr
/usr/share/httpd/manual/mod/mod_dav_lock.html.ja.utf8
/usr/share/httpd/manual/mod/mod_dbd.html
/usr/share/httpd/manual/mod/mod_dbd.html.en
/usr/share/httpd/manual/mod/mod_dbd.html.fr
/usr/share/httpd/manual/mod/mod_deflate.html
/usr/share/httpd/manual/mod/mod_deflate.html.en
/usr/share/httpd/manual/mod/mod_deflate.html.fr
/usr/share/httpd/manual/mod/mod_deflate.html.ja.utf8
/usr/share/httpd/manual/mod/mod_deflate.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_dialup.html
/usr/share/httpd/manual/mod/mod_dialup.html.en
/usr/share/httpd/manual/mod/mod_dialup.html.fr
/usr/share/httpd/manual/mod/mod_dir.html
/usr/share/httpd/manual/mod/mod_dir.html.en
/usr/share/httpd/manual/mod/mod_dir.html.fr
/usr/share/httpd/manual/mod/mod_dir.html.ja.utf8
/usr/share/httpd/manual/mod/mod_dir.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_dir.html.tr.utf8
/usr/share/httpd/manual/mod/mod_dumpio.html
/usr/share/httpd/manual/mod/mod_dumpio.html.en
/usr/share/httpd/manual/mod/mod_dumpio.html.fr
/usr/share/httpd/manual/mod/mod_dumpio.html.ja.utf8
/usr/share/httpd/manual/mod/mod_echo.html
/usr/share/httpd/manual/mod/mod_echo.html.en
/usr/share/httpd/manual/mod/mod_echo.html.fr
/usr/share/httpd/manual/mod/mod_echo.html.ja.utf8
/usr/share/httpd/manual/mod/mod_echo.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_env.html
/usr/share/httpd/manual/mod/mod_env.html.en
/usr/share/httpd/manual/mod/mod_env.html.fr
/usr/share/httpd/manual/mod/mod_env.html.ja.utf8
/usr/share/httpd/manual/mod/mod_env.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_env.html.tr.utf8
/usr/share/httpd/manual/mod/mod_example_hooks.html
/usr/share/httpd/manual/mod/mod_example_hooks.html.en
/usr/share/httpd/manual/mod/mod_example_hooks.html.fr
/usr/share/httpd/manual/mod/mod_example_hooks.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_expires.html
/usr/share/httpd/manual/mod/mod_expires.html.en
/usr/share/httpd/manual/mod/mod_expires.html.fr
/usr/share/httpd/manual/mod/mod_expires.html.ja.utf8
/usr/share/httpd/manual/mod/mod_expires.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_ext_filter.html
/usr/share/httpd/manual/mod/mod_ext_filter.html.en
/usr/share/httpd/manual/mod/mod_ext_filter.html.fr
/usr/share/httpd/manual/mod/mod_ext_filter.html.ja.utf8
/usr/share/httpd/manual/mod/mod_ext_filter.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_file_cache.html
/usr/share/httpd/manual/mod/mod_file_cache.html.en
/usr/share/httpd/manual/mod/mod_file_cache.html.fr
/usr/share/httpd/manual/mod/mod_file_cache.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_filter.html
/usr/share/httpd/manual/mod/mod_filter.html.en
/usr/share/httpd/manual/mod/mod_filter.html.fr
/usr/share/httpd/manual/mod/mod_headers.html
/usr/share/httpd/manual/mod/mod_headers.html.en
/usr/share/httpd/manual/mod/mod_headers.html.fr
/usr/share/httpd/manual/mod/mod_headers.html.ja.utf8
/usr/share/httpd/manual/mod/mod_headers.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_heartbeat.html
/usr/share/httpd/manual/mod/mod_heartbeat.html.en
/usr/share/httpd/manual/mod/mod_heartbeat.html.fr
/usr/share/httpd/manual/mod/mod_heartmonitor.html
/usr/share/httpd/manual/mod/mod_heartmonitor.html.en
/usr/share/httpd/manual/mod/mod_heartmonitor.html.fr
/usr/share/httpd/manual/mod/mod_http2.html
/usr/share/httpd/manual/mod/mod_http2.html.en
/usr/share/httpd/manual/mod/mod_ident.html
/usr/share/httpd/manual/mod/mod_ident.html.en
/usr/share/httpd/manual/mod/mod_ident.html.fr
/usr/share/httpd/manual/mod/mod_ident.html.ja.utf8
/usr/share/httpd/manual/mod/mod_ident.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_imagemap.html
/usr/share/httpd/manual/mod/mod_imagemap.html.en
/usr/share/httpd/manual/mod/mod_imagemap.html.fr
/usr/share/httpd/manual/mod/mod_imagemap.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_include.html
/usr/share/httpd/manual/mod/mod_include.html.en
/usr/share/httpd/manual/mod/mod_include.html.fr
/usr/share/httpd/manual/mod/mod_include.html.ja.utf8
/usr/share/httpd/manual/mod/mod_info.html
/usr/share/httpd/manual/mod/mod_info.html.en
/usr/share/httpd/manual/mod/mod_info.html.fr
/usr/share/httpd/manual/mod/mod_info.html.ja.utf8
/usr/share/httpd/manual/mod/mod_info.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_isapi.html
/usr/share/httpd/manual/mod/mod_isapi.html.en
/usr/share/httpd/manual/mod/mod_isapi.html.fr
/usr/share/httpd/manual/mod/mod_isapi.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_lbmethod_bybusyness.html
/usr/share/httpd/manual/mod/mod_lbmethod_bybusyness.html.en
/usr/share/httpd/manual/mod/mod_lbmethod_bybusyness.html.fr
/usr/share/httpd/manual/mod/mod_lbmethod_byrequests.html
/usr/share/httpd/manual/mod/mod_lbmethod_byrequests.html.en
/usr/share/httpd/manual/mod/mod_lbmethod_byrequests.html.fr
/usr/share/httpd/manual/mod/mod_lbmethod_bytraffic.html
/usr/share/httpd/manual/mod/mod_lbmethod_bytraffic.html.en
/usr/share/httpd/manual/mod/mod_lbmethod_bytraffic.html.fr
/usr/share/httpd/manual/mod/mod_lbmethod_heartbeat.html
/usr/share/httpd/manual/mod/mod_lbmethod_heartbeat.html.en
/usr/share/httpd/manual/mod/mod_lbmethod_heartbeat.html.fr
/usr/share/httpd/manual/mod/mod_ldap.html
/usr/share/httpd/manual/mod/mod_ldap.html.en
/usr/share/httpd/manual/mod/mod_ldap.html.fr
/usr/share/httpd/manual/mod/mod_log_config.html
/usr/share/httpd/manual/mod/mod_log_config.html.en
/usr/share/httpd/manual/mod/mod_log_config.html.fr
/usr/share/httpd/manual/mod/mod_log_config.html.ja.utf8
/usr/share/httpd/manual/mod/mod_log_config.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_log_config.html.tr.utf8
/usr/share/httpd/manual/mod/mod_log_debug.html
/usr/share/httpd/manual/mod/mod_log_debug.html.en
/usr/share/httpd/manual/mod/mod_log_debug.html.fr
/usr/share/httpd/manual/mod/mod_log_forensic.html
/usr/share/httpd/manual/mod/mod_log_forensic.html.en
/usr/share/httpd/manual/mod/mod_log_forensic.html.fr
/usr/share/httpd/manual/mod/mod_log_forensic.html.ja.utf8
/usr/share/httpd/manual/mod/mod_log_forensic.html.tr.utf8
/usr/share/httpd/manual/mod/mod_logio.html
/usr/share/httpd/manual/mod/mod_logio.html.en
/usr/share/httpd/manual/mod/mod_logio.html.fr
/usr/share/httpd/manual/mod/mod_logio.html.ja.utf8
/usr/share/httpd/manual/mod/mod_logio.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_logio.html.tr.utf8
/usr/share/httpd/manual/mod/mod_lua.html
/usr/share/httpd/manual/mod/mod_lua.html.en
/usr/share/httpd/manual/mod/mod_lua.html.fr
/usr/share/httpd/manual/mod/mod_macro.html
/usr/share/httpd/manual/mod/mod_macro.html.en
/usr/share/httpd/manual/mod/mod_macro.html.fr
/usr/share/httpd/manual/mod/mod_mime.html
/usr/share/httpd/manual/mod/mod_mime.html.en
/usr/share/httpd/manual/mod/mod_mime.html.fr
/usr/share/httpd/manual/mod/mod_mime.html.ja.utf8
/usr/share/httpd/manual/mod/mod_mime_magic.html
/usr/share/httpd/manual/mod/mod_mime_magic.html.en
/usr/share/httpd/manual/mod/mod_mime_magic.html.fr
/usr/share/httpd/manual/mod/mod_negotiation.html
/usr/share/httpd/manual/mod/mod_negotiation.html.en
/usr/share/httpd/manual/mod/mod_negotiation.html.fr
/usr/share/httpd/manual/mod/mod_negotiation.html.ja.utf8
/usr/share/httpd/manual/mod/mod_nw_ssl.html
/usr/share/httpd/manual/mod/mod_nw_ssl.html.en
/usr/share/httpd/manual/mod/mod_nw_ssl.html.fr
/usr/share/httpd/manual/mod/mod_privileges.html
/usr/share/httpd/manual/mod/mod_privileges.html.en
/usr/share/httpd/manual/mod/mod_privileges.html.fr
/usr/share/httpd/manual/mod/mod_proxy.html
/usr/share/httpd/manual/mod/mod_proxy.html.en
/usr/share/httpd/manual/mod/mod_proxy.html.fr
/usr/share/httpd/manual/mod/mod_proxy.html.ja.utf8
/usr/share/httpd/manual/mod/mod_proxy_ajp.html
/usr/share/httpd/manual/mod/mod_proxy_ajp.html.en
/usr/share/httpd/manual/mod/mod_proxy_ajp.html.fr
/usr/share/httpd/manual/mod/mod_proxy_ajp.html.ja.utf8
/usr/share/httpd/manual/mod/mod_proxy_balancer.html
/usr/share/httpd/manual/mod/mod_proxy_balancer.html.en
/usr/share/httpd/manual/mod/mod_proxy_balancer.html.fr
/usr/share/httpd/manual/mod/mod_proxy_balancer.html.ja.utf8
/usr/share/httpd/manual/mod/mod_proxy_connect.html
/usr/share/httpd/manual/mod/mod_proxy_connect.html.en
/usr/share/httpd/manual/mod/mod_proxy_connect.html.fr
/usr/share/httpd/manual/mod/mod_proxy_connect.html.ja.utf8
/usr/share/httpd/manual/mod/mod_proxy_express.html
/usr/share/httpd/manual/mod/mod_proxy_express.html.en
/usr/share/httpd/manual/mod/mod_proxy_express.html.fr
/usr/share/httpd/manual/mod/mod_proxy_fcgi.html
/usr/share/httpd/manual/mod/mod_proxy_fcgi.html.en
/usr/share/httpd/manual/mod/mod_proxy_fcgi.html.fr
/usr/share/httpd/manual/mod/mod_proxy_fdpass.html
/usr/share/httpd/manual/mod/mod_proxy_fdpass.html.en
/usr/share/httpd/manual/mod/mod_proxy_fdpass.html.fr
/usr/share/httpd/manual/mod/mod_proxy_ftp.html
/usr/share/httpd/manual/mod/mod_proxy_ftp.html.en
/usr/share/httpd/manual/mod/mod_proxy_ftp.html.fr
/usr/share/httpd/manual/mod/mod_proxy_html.html
/usr/share/httpd/manual/mod/mod_proxy_html.html.en
/usr/share/httpd/manual/mod/mod_proxy_html.html.fr
/usr/share/httpd/manual/mod/mod_proxy_http.html
/usr/share/httpd/manual/mod/mod_proxy_http.html.en
/usr/share/httpd/manual/mod/mod_proxy_http.html.fr
/usr/share/httpd/manual/mod/mod_proxy_scgi.html
/usr/share/httpd/manual/mod/mod_proxy_scgi.html.en
/usr/share/httpd/manual/mod/mod_proxy_scgi.html.fr
/usr/share/httpd/manual/mod/mod_proxy_wstunnel.html
/usr/share/httpd/manual/mod/mod_proxy_wstunnel.html.en
/usr/share/httpd/manual/mod/mod_ratelimit.html
/usr/share/httpd/manual/mod/mod_ratelimit.html.en
/usr/share/httpd/manual/mod/mod_ratelimit.html.fr
/usr/share/httpd/manual/mod/mod_reflector.html
/usr/share/httpd/manual/mod/mod_reflector.html.en
/usr/share/httpd/manual/mod/mod_reflector.html.fr
/usr/share/httpd/manual/mod/mod_remoteip.html
/usr/share/httpd/manual/mod/mod_remoteip.html.en
/usr/share/httpd/manual/mod/mod_remoteip.html.fr
/usr/share/httpd/manual/mod/mod_reqtimeout.html
/usr/share/httpd/manual/mod/mod_reqtimeout.html.en
/usr/share/httpd/manual/mod/mod_reqtimeout.html.fr
/usr/share/httpd/manual/mod/mod_request.html
/usr/share/httpd/manual/mod/mod_request.html.en
/usr/share/httpd/manual/mod/mod_request.html.fr
/usr/share/httpd/manual/mod/mod_request.html.tr.utf8
/usr/share/httpd/manual/mod/mod_rewrite.html
/usr/share/httpd/manual/mod/mod_rewrite.html.en
/usr/share/httpd/manual/mod/mod_rewrite.html.fr
/usr/share/httpd/manual/mod/mod_sed.html
/usr/share/httpd/manual/mod/mod_sed.html.en
/usr/share/httpd/manual/mod/mod_sed.html.fr
/usr/share/httpd/manual/mod/mod_session.html
/usr/share/httpd/manual/mod/mod_session.html.en
/usr/share/httpd/manual/mod/mod_session.html.fr
/usr/share/httpd/manual/mod/mod_session_cookie.html
/usr/share/httpd/manual/mod/mod_session_cookie.html.en
/usr/share/httpd/manual/mod/mod_session_cookie.html.fr
/usr/share/httpd/manual/mod/mod_session_crypto.html
/usr/share/httpd/manual/mod/mod_session_crypto.html.en
/usr/share/httpd/manual/mod/mod_session_crypto.html.fr
/usr/share/httpd/manual/mod/mod_session_dbd.html
/usr/share/httpd/manual/mod/mod_session_dbd.html.en
/usr/share/httpd/manual/mod/mod_session_dbd.html.fr
/usr/share/httpd/manual/mod/mod_setenvif.html
/usr/share/httpd/manual/mod/mod_setenvif.html.en
/usr/share/httpd/manual/mod/mod_setenvif.html.fr
/usr/share/httpd/manual/mod/mod_setenvif.html.ja.utf8
/usr/share/httpd/manual/mod/mod_setenvif.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_setenvif.html.tr.utf8
/usr/share/httpd/manual/mod/mod_slotmem_plain.html
/usr/share/httpd/manual/mod/mod_slotmem_plain.html.en
/usr/share/httpd/manual/mod/mod_slotmem_plain.html.fr
/usr/share/httpd/manual/mod/mod_slotmem_shm.html
/usr/share/httpd/manual/mod/mod_slotmem_shm.html.en
/usr/share/httpd/manual/mod/mod_slotmem_shm.html.fr
/usr/share/httpd/manual/mod/mod_so.html
/usr/share/httpd/manual/mod/mod_so.html.en
/usr/share/httpd/manual/mod/mod_so.html.fr
/usr/share/httpd/manual/mod/mod_so.html.ja.utf8
/usr/share/httpd/manual/mod/mod_so.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_so.html.tr.utf8
/usr/share/httpd/manual/mod/mod_socache_dbm.html
/usr/share/httpd/manual/mod/mod_socache_dbm.html.en
/usr/share/httpd/manual/mod/mod_socache_dbm.html.fr
/usr/share/httpd/manual/mod/mod_socache_dc.html
/usr/share/httpd/manual/mod/mod_socache_dc.html.en
/usr/share/httpd/manual/mod/mod_socache_dc.html.fr
/usr/share/httpd/manual/mod/mod_socache_memcache.html
/usr/share/httpd/manual/mod/mod_socache_memcache.html.en
/usr/share/httpd/manual/mod/mod_socache_memcache.html.fr
/usr/share/httpd/manual/mod/mod_socache_shmcb.html
/usr/share/httpd/manual/mod/mod_socache_shmcb.html.en
/usr/share/httpd/manual/mod/mod_socache_shmcb.html.fr
/usr/share/httpd/manual/mod/mod_speling.html
/usr/share/httpd/manual/mod/mod_speling.html.en
/usr/share/httpd/manual/mod/mod_speling.html.fr
/usr/share/httpd/manual/mod/mod_speling.html.ja.utf8
/usr/share/httpd/manual/mod/mod_speling.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_ssl.html
/usr/share/httpd/manual/mod/mod_ssl.html.en
/usr/share/httpd/manual/mod/mod_ssl.html.fr
/usr/share/httpd/manual/mod/mod_status.html
/usr/share/httpd/manual/mod/mod_status.html.en
/usr/share/httpd/manual/mod/mod_status.html.fr
/usr/share/httpd/manual/mod/mod_status.html.ja.utf8
/usr/share/httpd/manual/mod/mod_status.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_status.html.tr.utf8
/usr/share/httpd/manual/mod/mod_substitute.html
/usr/share/httpd/manual/mod/mod_substitute.html.en
/usr/share/httpd/manual/mod/mod_substitute.html.fr
/usr/share/httpd/manual/mod/mod_suexec.html
/usr/share/httpd/manual/mod/mod_suexec.html.en
/usr/share/httpd/manual/mod/mod_suexec.html.fr
/usr/share/httpd/manual/mod/mod_suexec.html.ja.utf8
/usr/share/httpd/manual/mod/mod_suexec.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_suexec.html.tr.utf8
/usr/share/httpd/manual/mod/mod_unique_id.html
/usr/share/httpd/manual/mod/mod_unique_id.html.en
/usr/share/httpd/manual/mod/mod_unique_id.html.fr
/usr/share/httpd/manual/mod/mod_unique_id.html.ja.utf8
/usr/share/httpd/manual/mod/mod_unique_id.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_unixd.html
/usr/share/httpd/manual/mod/mod_unixd.html.en
/usr/share/httpd/manual/mod/mod_unixd.html.fr
/usr/share/httpd/manual/mod/mod_unixd.html.tr.utf8
/usr/share/httpd/manual/mod/mod_userdir.html
/usr/share/httpd/manual/mod/mod_userdir.html.en
/usr/share/httpd/manual/mod/mod_userdir.html.fr
/usr/share/httpd/manual/mod/mod_userdir.html.ja.utf8
/usr/share/httpd/manual/mod/mod_userdir.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_userdir.html.tr.utf8
/usr/share/httpd/manual/mod/mod_usertrack.html
/usr/share/httpd/manual/mod/mod_usertrack.html.en
/usr/share/httpd/manual/mod/mod_usertrack.html.fr
/usr/share/httpd/manual/mod/mod_version.html
/usr/share/httpd/manual/mod/mod_version.html.en
/usr/share/httpd/manual/mod/mod_version.html.ja.utf8
/usr/share/httpd/manual/mod/mod_version.html.ko.euc-kr
/usr/share/httpd/manual/mod/mod_vhost_alias.html
/usr/share/httpd/manual/mod/mod_vhost_alias.html.en
/usr/share/httpd/manual/mod/mod_vhost_alias.html.fr
/usr/share/httpd/manual/mod/mod_vhost_alias.html.tr.utf8
/usr/share/httpd/manual/mod/mod_watchdog.html
/usr/share/httpd/manual/mod/mod_watchdog.html.en
/usr/share/httpd/manual/mod/mod_xml2enc.html
/usr/share/httpd/manual/mod/mod_xml2enc.html.en
/usr/share/httpd/manual/mod/mod_xml2enc.html.fr
/usr/share/httpd/manual/mod/module-dict.html
/usr/share/httpd/manual/mod/module-dict.html.en
/usr/share/httpd/manual/mod/module-dict.html.fr
/usr/share/httpd/manual/mod/module-dict.html.ja.utf8
/usr/share/httpd/manual/mod/module-dict.html.ko.euc-kr
/usr/share/httpd/manual/mod/module-dict.html.tr.utf8
/usr/share/httpd/manual/mod/mpm_common.html
/usr/share/httpd/manual/mod/mpm_common.html.de
/usr/share/httpd/manual/mod/mpm_common.html.en
/usr/share/httpd/manual/mod/mpm_common.html.fr
/usr/share/httpd/manual/mod/mpm_common.html.ja.utf8
/usr/share/httpd/manual/mod/mpm_common.html.tr.utf8
/usr/share/httpd/manual/mod/mpm_netware.html
/usr/share/httpd/manual/mod/mpm_netware.html.en
/usr/share/httpd/manual/mod/mpm_netware.html.fr
/usr/share/httpd/manual/mod/mpm_winnt.html
/usr/share/httpd/manual/mod/mpm_winnt.html.de
/usr/share/httpd/manual/mod/mpm_winnt.html.en
/usr/share/httpd/manual/mod/mpm_winnt.html.fr
/usr/share/httpd/manual/mod/mpm_winnt.html.ja.utf8
/usr/share/httpd/manual/mod/mpmt_os2.html
/usr/share/httpd/manual/mod/mpmt_os2.html.en
/usr/share/httpd/manual/mod/mpmt_os2.html.fr
/usr/share/httpd/manual/mod/prefork.html
/usr/share/httpd/manual/mod/prefork.html.de
/usr/share/httpd/manual/mod/prefork.html.en
/usr/share/httpd/manual/mod/prefork.html.fr
/usr/share/httpd/manual/mod/prefork.html.ja.utf8
/usr/share/httpd/manual/mod/prefork.html.tr.utf8
/usr/share/httpd/manual/mod/quickreference.html
/usr/share/httpd/manual/mod/quickreference.html.de
/usr/share/httpd/manual/mod/quickreference.html.en
/usr/share/httpd/manual/mod/quickreference.html.es
/usr/share/httpd/manual/mod/quickreference.html.fr
/usr/share/httpd/manual/mod/quickreference.html.ja.utf8
/usr/share/httpd/manual/mod/quickreference.html.ko.euc-kr
/usr/share/httpd/manual/mod/quickreference.html.tr.utf8
/usr/share/httpd/manual/mod/quickreference.html.zh-cn.utf8
/usr/share/httpd/manual/mod/worker.html
/usr/share/httpd/manual/mod/worker.html.de
/usr/share/httpd/manual/mod/worker.html.en
/usr/share/httpd/manual/mod/worker.html.fr
/usr/share/httpd/manual/mod/worker.html.ja.utf8
/usr/share/httpd/manual/mod/worker.html.tr.utf8
/usr/share/httpd/manual/mpm.html
/usr/share/httpd/manual/mpm.html.de
/usr/share/httpd/manual/mpm.html.en
/usr/share/httpd/manual/mpm.html.es
/usr/share/httpd/manual/mpm.html.fr
/usr/share/httpd/manual/mpm.html.ja.utf8
/usr/share/httpd/manual/mpm.html.ko.euc-kr
/usr/share/httpd/manual/mpm.html.tr.utf8
/usr/share/httpd/manual/mpm.html.zh-cn.utf8
/usr/share/httpd/manual/new_features_2_0.html
/usr/share/httpd/manual/new_features_2_0.html.de
/usr/share/httpd/manual/new_features_2_0.html.en
/usr/share/httpd/manual/new_features_2_0.html.fr
/usr/share/httpd/manual/new_features_2_0.html.ja.utf8
/usr/share/httpd/manual/new_features_2_0.html.ko.euc-kr
/usr/share/httpd/manual/new_features_2_0.html.pt-br
/usr/share/httpd/manual/new_features_2_0.html.ru.koi8-r
/usr/share/httpd/manual/new_features_2_0.html.tr.utf8
/usr/share/httpd/manual/new_features_2_2.html
/usr/share/httpd/manual/new_features_2_2.html.en
/usr/share/httpd/manual/new_features_2_2.html.fr
/usr/share/httpd/manual/new_features_2_2.html.ko.euc-kr
/usr/share/httpd/manual/new_features_2_2.html.pt-br
/usr/share/httpd/manual/new_features_2_2.html.tr.utf8
/usr/share/httpd/manual/new_features_2_4.html
/usr/share/httpd/manual/new_features_2_4.html.en
/usr/share/httpd/manual/new_features_2_4.html.fr
/usr/share/httpd/manual/new_features_2_4.html.tr.utf8
/usr/share/httpd/manual/platform/ebcdic.html
/usr/share/httpd/manual/platform/ebcdic.html.en
/usr/share/httpd/manual/platform/ebcdic.html.ko.euc-kr
/usr/share/httpd/manual/platform/index.html
/usr/share/httpd/manual/platform/index.html.en
/usr/share/httpd/manual/platform/index.html.fr
/usr/share/httpd/manual/platform/index.html.ko.euc-kr
/usr/share/httpd/manual/platform/index.html.zh-cn.utf8
/usr/share/httpd/manual/platform/netware.html
/usr/share/httpd/manual/platform/netware.html.en
/usr/share/httpd/manual/platform/netware.html.fr
/usr/share/httpd/manual/platform/netware.html.ko.euc-kr
/usr/share/httpd/manual/platform/perf-hp.html
/usr/share/httpd/manual/platform/perf-hp.html.en
/usr/share/httpd/manual/platform/perf-hp.html.fr
/usr/share/httpd/manual/platform/perf-hp.html.ko.euc-kr
/usr/share/httpd/manual/platform/rpm.html
/usr/share/httpd/manual/platform/rpm.html.en
/usr/share/httpd/manual/platform/win_compiling.html
/usr/share/httpd/manual/platform/win_compiling.html.en
/usr/share/httpd/manual/platform/win_compiling.html.fr
/usr/share/httpd/manual/platform/win_compiling.html.ko.euc-kr
/usr/share/httpd/manual/platform/windows.html
/usr/share/httpd/manual/platform/windows.html.en
/usr/share/httpd/manual/platform/windows.html.fr
/usr/share/httpd/manual/platform/windows.html.ko.euc-kr
/usr/share/httpd/manual/programs/ab.html
/usr/share/httpd/manual/programs/ab.html.en
/usr/share/httpd/manual/programs/ab.html.fr
/usr/share/httpd/manual/programs/ab.html.ko.euc-kr
/usr/share/httpd/manual/programs/ab.html.tr.utf8
/usr/share/httpd/manual/programs/apachectl.html
/usr/share/httpd/manual/programs/apachectl.html.en
/usr/share/httpd/manual/programs/apachectl.html.fr
/usr/share/httpd/manual/programs/apachectl.html.ko.euc-kr
/usr/share/httpd/manual/programs/apachectl.html.tr.utf8
/usr/share/httpd/manual/programs/apxs.html
/usr/share/httpd/manual/programs/apxs.html.en
/usr/share/httpd/manual/programs/apxs.html.fr
/usr/share/httpd/manual/programs/apxs.html.ko.euc-kr
/usr/share/httpd/manual/programs/apxs.html.tr.utf8
/usr/share/httpd/manual/programs/configure.html
/usr/share/httpd/manual/programs/configure.html.en
/usr/share/httpd/manual/programs/configure.html.fr
/usr/share/httpd/manual/programs/configure.html.ko.euc-kr
/usr/share/httpd/manual/programs/configure.html.tr.utf8
/usr/share/httpd/manual/programs/dbmmanage.html
/usr/share/httpd/manual/programs/dbmmanage.html.en
/usr/share/httpd/manual/programs/dbmmanage.html.fr
/usr/share/httpd/manual/programs/dbmmanage.html.ko.euc-kr
/usr/share/httpd/manual/programs/dbmmanage.html.tr.utf8
/usr/share/httpd/manual/programs/fcgistarter.html
/usr/share/httpd/manual/programs/fcgistarter.html.en
/usr/share/httpd/manual/programs/fcgistarter.html.fr
/usr/share/httpd/manual/programs/fcgistarter.html.tr.utf8
/usr/share/httpd/manual/programs/htcacheclean.html
/usr/share/httpd/manual/programs/htcacheclean.html.en
/usr/share/httpd/manual/programs/htcacheclean.html.fr
/usr/share/httpd/manual/programs/htcacheclean.html.ko.euc-kr
/usr/share/httpd/manual/programs/htcacheclean.html.tr.utf8
/usr/share/httpd/manual/programs/htdbm.html
/usr/share/httpd/manual/programs/htdbm.html.en
/usr/share/httpd/manual/programs/htdbm.html.fr
/usr/share/httpd/manual/programs/htdbm.html.tr.utf8
/usr/share/httpd/manual/programs/htdigest.html
/usr/share/httpd/manual/programs/htdigest.html.en
/usr/share/httpd/manual/programs/htdigest.html.fr
/usr/share/httpd/manual/programs/htdigest.html.ko.euc-kr
/usr/share/httpd/manual/programs/htdigest.html.tr.utf8
/usr/share/httpd/manual/programs/htpasswd.html
/usr/share/httpd/manual/programs/htpasswd.html.en
/usr/share/httpd/manual/programs/htpasswd.html.fr
/usr/share/httpd/manual/programs/htpasswd.html.ko.euc-kr
/usr/share/httpd/manual/programs/htpasswd.html.tr.utf8
/usr/share/httpd/manual/programs/httpd.html
/usr/share/httpd/manual/programs/httpd.html.en
/usr/share/httpd/manual/programs/httpd.html.fr
/usr/share/httpd/manual/programs/httpd.html.ko.euc-kr
/usr/share/httpd/manual/programs/httpd.html.tr.utf8
/usr/share/httpd/manual/programs/httxt2dbm.html
/usr/share/httpd/manual/programs/httxt2dbm.html.en
/usr/share/httpd/manual/programs/httxt2dbm.html.fr
/usr/share/httpd/manual/programs/httxt2dbm.html.tr.utf8
/usr/share/httpd/manual/programs/index.html
/usr/share/httpd/manual/programs/index.html.en
/usr/share/httpd/manual/programs/index.html.es
/usr/share/httpd/manual/programs/index.html.fr
/usr/share/httpd/manual/programs/index.html.ko.euc-kr
/usr/share/httpd/manual/programs/index.html.tr.utf8
/usr/share/httpd/manual/programs/index.html.zh-cn.utf8
/usr/share/httpd/manual/programs/log_server_status.html
/usr/share/httpd/manual/programs/log_server_status.html.en
/usr/share/httpd/manual/programs/logresolve.html
/usr/share/httpd/manual/programs/logresolve.html.en
/usr/share/httpd/manual/programs/logresolve.html.fr
/usr/share/httpd/manual/programs/logresolve.html.ko.euc-kr
/usr/share/httpd/manual/programs/logresolve.html.tr.utf8
/usr/share/httpd/manual/programs/other.html
/usr/share/httpd/manual/programs/other.html.en
/usr/share/httpd/manual/programs/other.html.fr
/usr/share/httpd/manual/programs/other.html.ko.euc-kr
/usr/share/httpd/manual/programs/other.html.tr.utf8
/usr/share/httpd/manual/programs/rotatelogs.html
/usr/share/httpd/manual/programs/rotatelogs.html.en
/usr/share/httpd/manual/programs/rotatelogs.html.fr
/usr/share/httpd/manual/programs/rotatelogs.html.ko.euc-kr
/usr/share/httpd/manual/programs/rotatelogs.html.tr.utf8
/usr/share/httpd/manual/programs/split-logfile.html
/usr/share/httpd/manual/programs/split-logfile.html.en
/usr/share/httpd/manual/programs/suexec.html
/usr/share/httpd/manual/programs/suexec.html.en
/usr/share/httpd/manual/programs/suexec.html.ko.euc-kr
/usr/share/httpd/manual/programs/suexec.html.tr.utf8
/usr/share/httpd/manual/rewrite/access.html
/usr/share/httpd/manual/rewrite/access.html.en
/usr/share/httpd/manual/rewrite/access.html.fr
/usr/share/httpd/manual/rewrite/advanced.html
/usr/share/httpd/manual/rewrite/advanced.html.en
/usr/share/httpd/manual/rewrite/advanced.html.fr
/usr/share/httpd/manual/rewrite/avoid.html
/usr/share/httpd/manual/rewrite/avoid.html.en
/usr/share/httpd/manual/rewrite/avoid.html.fr
/usr/share/httpd/manual/rewrite/flags.html
/usr/share/httpd/manual/rewrite/flags.html.en
/usr/share/httpd/manual/rewrite/flags.html.fr
/usr/share/httpd/manual/rewrite/htaccess.html
/usr/share/httpd/manual/rewrite/htaccess.html.en
/usr/share/httpd/manual/rewrite/htaccess.html.fr
/usr/share/httpd/manual/rewrite/index.html
/usr/share/httpd/manual/rewrite/index.html.en
/usr/share/httpd/manual/rewrite/index.html.fr
/usr/share/httpd/manual/rewrite/index.html.tr.utf8
/usr/share/httpd/manual/rewrite/index.html.zh-cn.utf8
/usr/share/httpd/manual/rewrite/intro.html
/usr/share/httpd/manual/rewrite/intro.html.en
/usr/share/httpd/manual/rewrite/intro.html.fr
/usr/share/httpd/manual/rewrite/proxy.html
/usr/share/httpd/manual/rewrite/proxy.html.en
/usr/share/httpd/manual/rewrite/proxy.html.fr
/usr/share/httpd/manual/rewrite/remapping.html
/usr/share/httpd/manual/rewrite/remapping.html.en
/usr/share/httpd/manual/rewrite/remapping.html.fr
/usr/share/httpd/manual/rewrite/rewritemap.html
/usr/share/httpd/manual/rewrite/rewritemap.html.en
/usr/share/httpd/manual/rewrite/rewritemap.html.fr
/usr/share/httpd/manual/rewrite/tech.html
/usr/share/httpd/manual/rewrite/tech.html.en
/usr/share/httpd/manual/rewrite/tech.html.fr
/usr/share/httpd/manual/rewrite/vhosts.html
/usr/share/httpd/manual/rewrite/vhosts.html.en
/usr/share/httpd/manual/rewrite/vhosts.html.fr
/usr/share/httpd/manual/sections.html
/usr/share/httpd/manual/sections.html.en
/usr/share/httpd/manual/sections.html.fr
/usr/share/httpd/manual/sections.html.ja.utf8
/usr/share/httpd/manual/sections.html.ko.euc-kr
/usr/share/httpd/manual/sections.html.tr.utf8
/usr/share/httpd/manual/server-wide.html
/usr/share/httpd/manual/server-wide.html.en
/usr/share/httpd/manual/server-wide.html.fr
/usr/share/httpd/manual/server-wide.html.ja.utf8
/usr/share/httpd/manual/server-wide.html.ko.euc-kr
/usr/share/httpd/manual/server-wide.html.tr.utf8
/usr/share/httpd/manual/sitemap.html
/usr/share/httpd/manual/sitemap.html.de
/usr/share/httpd/manual/sitemap.html.en
/usr/share/httpd/manual/sitemap.html.es
/usr/share/httpd/manual/sitemap.html.fr
/usr/share/httpd/manual/sitemap.html.ja.utf8
/usr/share/httpd/manual/sitemap.html.ko.euc-kr
/usr/share/httpd/manual/sitemap.html.tr.utf8
/usr/share/httpd/manual/sitemap.html.zh-cn.utf8
/usr/share/httpd/manual/socache.html
/usr/share/httpd/manual/socache.html.en
/usr/share/httpd/manual/socache.html.fr
/usr/share/httpd/manual/ssl/index.html
/usr/share/httpd/manual/ssl/index.html.en
/usr/share/httpd/manual/ssl/index.html.fr
/usr/share/httpd/manual/ssl/index.html.ja.utf8
/usr/share/httpd/manual/ssl/index.html.tr.utf8
/usr/share/httpd/manual/ssl/index.html.zh-cn.utf8
/usr/share/httpd/manual/ssl/ssl_compat.html
/usr/share/httpd/manual/ssl/ssl_compat.html.en
/usr/share/httpd/manual/ssl/ssl_compat.html.fr
/usr/share/httpd/manual/ssl/ssl_faq.html
/usr/share/httpd/manual/ssl/ssl_faq.html.en
/usr/share/httpd/manual/ssl/ssl_faq.html.fr
/usr/share/httpd/manual/ssl/ssl_howto.html
/usr/share/httpd/manual/ssl/ssl_howto.html.en
/usr/share/httpd/manual/ssl/ssl_howto.html.fr
/usr/share/httpd/manual/ssl/ssl_intro.html
/usr/share/httpd/manual/ssl/ssl_intro.html.en
/usr/share/httpd/manual/ssl/ssl_intro.html.fr
/usr/share/httpd/manual/ssl/ssl_intro.html.ja.utf8
/usr/share/httpd/manual/stopping.html
/usr/share/httpd/manual/stopping.html.de
/usr/share/httpd/manual/stopping.html.en
/usr/share/httpd/manual/stopping.html.es
/usr/share/httpd/manual/stopping.html.fr
/usr/share/httpd/manual/stopping.html.ja.utf8
/usr/share/httpd/manual/stopping.html.ko.euc-kr
/usr/share/httpd/manual/stopping.html.tr.utf8
/usr/share/httpd/manual/style/build.properties
/usr/share/httpd/manual/style/common.dtd
/usr/share/httpd/manual/style/css/manual-chm.css
/usr/share/httpd/manual/style/css/manual-loose-100pc.css
/usr/share/httpd/manual/style/css/manual-print.css
/usr/share/httpd/manual/style/css/manual-zip-100pc.css
/usr/share/httpd/manual/style/css/manual-zip.css
/usr/share/httpd/manual/style/css/manual.css
/usr/share/httpd/manual/style/css/prettify.css
/usr/share/httpd/manual/style/faq.dtd
/usr/share/httpd/manual/style/lang.dtd
/usr/share/httpd/manual/style/latex/atbeginend.sty
/usr/share/httpd/manual/style/manualpage.dtd
/usr/share/httpd/manual/style/modulesynopsis.dtd
/usr/share/httpd/manual/style/scripts/MINIFY
/usr/share/httpd/manual/style/scripts/prettify.js
/usr/share/httpd/manual/style/scripts/prettify.min.js
/usr/share/httpd/manual/style/sitemap.dtd
/usr/share/httpd/manual/style/version.ent
/usr/share/httpd/manual/suexec.html
/usr/share/httpd/manual/suexec.html.en
/usr/share/httpd/manual/suexec.html.fr
/usr/share/httpd/manual/suexec.html.ja.utf8
/usr/share/httpd/manual/suexec.html.ko.euc-kr
/usr/share/httpd/manual/suexec.html.tr.utf8
/usr/share/httpd/manual/upgrading.html
/usr/share/httpd/manual/upgrading.html.en
/usr/share/httpd/manual/upgrading.html.fr
/usr/share/httpd/manual/urlmapping.html
/usr/share/httpd/manual/urlmapping.html.en
/usr/share/httpd/manual/urlmapping.html.fr
/usr/share/httpd/manual/urlmapping.html.ja.utf8
/usr/share/httpd/manual/urlmapping.html.ko.euc-kr
/usr/share/httpd/manual/urlmapping.html.tr.utf8
/usr/share/httpd/manual/vhosts/details.html
/usr/share/httpd/manual/vhosts/details.html.en
/usr/share/httpd/manual/vhosts/details.html.fr
/usr/share/httpd/manual/vhosts/details.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/details.html.tr.utf8
/usr/share/httpd/manual/vhosts/examples.html
/usr/share/httpd/manual/vhosts/examples.html.en
/usr/share/httpd/manual/vhosts/examples.html.fr
/usr/share/httpd/manual/vhosts/examples.html.ja.utf8
/usr/share/httpd/manual/vhosts/examples.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/examples.html.tr.utf8
/usr/share/httpd/manual/vhosts/fd-limits.html
/usr/share/httpd/manual/vhosts/fd-limits.html.en
/usr/share/httpd/manual/vhosts/fd-limits.html.fr
/usr/share/httpd/manual/vhosts/fd-limits.html.ja.utf8
/usr/share/httpd/manual/vhosts/fd-limits.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/fd-limits.html.tr.utf8
/usr/share/httpd/manual/vhosts/index.html
/usr/share/httpd/manual/vhosts/index.html.de
/usr/share/httpd/manual/vhosts/index.html.en
/usr/share/httpd/manual/vhosts/index.html.fr
/usr/share/httpd/manual/vhosts/index.html.ja.utf8
/usr/share/httpd/manual/vhosts/index.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/index.html.tr.utf8
/usr/share/httpd/manual/vhosts/index.html.zh-cn.utf8
/usr/share/httpd/manual/vhosts/ip-based.html
/usr/share/httpd/manual/vhosts/ip-based.html.en
/usr/share/httpd/manual/vhosts/ip-based.html.fr
/usr/share/httpd/manual/vhosts/ip-based.html.ja.utf8
/usr/share/httpd/manual/vhosts/ip-based.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/ip-based.html.tr.utf8
/usr/share/httpd/manual/vhosts/mass.html
/usr/share/httpd/manual/vhosts/mass.html.en
/usr/share/httpd/manual/vhosts/mass.html.fr
/usr/share/httpd/manual/vhosts/mass.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/mass.html.tr.utf8
/usr/share/httpd/manual/vhosts/name-based.html
/usr/share/httpd/manual/vhosts/name-based.html.de
/usr/share/httpd/manual/vhosts/name-based.html.en
/usr/share/httpd/manual/vhosts/name-based.html.fr
/usr/share/httpd/manual/vhosts/name-based.html.ja.utf8
/usr/share/httpd/manual/vhosts/name-based.html.ko.euc-kr
/usr/share/httpd/manual/vhosts/name-based.html.tr.utf8

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
