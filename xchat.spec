%define	build_plf 0

%if %build_plf
%define	distsuffix plf
%endif 

%{?_with_plf: %{expand: %%global build_plf 1}}

%define	perl_version %(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)

Summary:	A GTK+ IRC client
Name:		xchat
Version:	2.8.8
Release:	11
Group:		Networking/IRC
License:	GPLv2+
Url:		http://www.xchat.org
Source0:	http://www.xchat.org/files/source/2.8/%{name}-%{version}.tar.bz2
Patch0:		xchat-2.6.4-ctcp_version.patch
Patch1:		xchat-2.0.8-nicksuffix.patch
Patch2:		xchat-2.6.1-servlist.patch
Patch3:		xchat-2.8.6-CVE-2009-0315-debian.patch
Patch4:		xchat-2.8.8-autoconf.patch
# fedora patches
Patch100:	xchat-1.8.7-use-sysconf-to-detect-cpus.patch
Patch101:	xchat-2.8.4-disable-tray-icon-by-default.patch
Patch102:	xchat-2.8.6-default-utf8.patch
Patch103:	xchat-2.8.6-change-page-activity.patch
Patch104:	xchat-2.8.8-freenode-ports.diff
Patch105:	xchat-2.8.8-libnotify07.patch
Patch106:	xchat-2.8.8-link-against-libnotify.patch
Patch107:	fixglib.patch
BuildRequires:	bison
BuildRequires:	desktop-file-utils
BuildRequires:	GConf2
BuildRequires:	imagemagick
BuildRequires:	gettext-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(libnotify)
BuildRequires:	pkgconfig(libntlm)
BuildRequires:	pkgconfig(libsexy)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(tcl)
%if %build_plf
BuildRequires:	socks5-devel
%endif
Provides:	xchat-dbus = %{version}-%{release}
# To get the balloon alerts working
Requires:	libnotify

%description
X-Chat is yet another IRC client for the X Window System, using the Gtk+
toolkit. It is pretty easy to use compared to the other Gtk+ IRC clients and
the interface is quite nicely designed.

%package devel
Summary:	XChat header for plugin development
Group:		Development/C

%description devel
This package contains xchat-plugin.h needed to build external plugins.

%package perl
Summary:	XChat Perl plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}-%{release}
Requires:	perl-base = %perl_version

%description perl
Provides Perl scripting capability to XChat.

%package python
Summary:	XChat Python plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}-%{release}

%description python
Provides Python scripting capability to XChat.

%package tcl
Summary:	XChat TCL plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}-%{release}

%description tcl
Provides tcl scripting capability to XChat.

%prep

%setup -q
%patch0
%patch1 -p1
%patch2 -p0 -b .default_server
%patch3 -p1 -b .cve-2009-0315
%patch4 -p0 -b .autoconf

# fedora patches
%patch100 -p0 -b .use-sysconf-to-detect-cpus
%patch101 -p1 -b .tray-icon
%patch102 -p1 -b .default-utf8
%patch103 -p1 -b .active-channel-switch
%patch104 -p0 -b .freenode-ports
%patch105 -p1 -b .libnotify07
%patch106 -p1 -b .link-against-libnotify
%patch107 -p1 -b .fixglib

# fix build against latest GTK+
sed -i -e 's/#define GTK_DISABLE_DEPRECATED//g' src/fe-gtk/*.c

find . -name Makefile.in |xargs sed -i -e 's,configure.in,configure.ac,g'
./autogen.sh

%build
# (tpg) disable Xft as it breaks RTL languages
# use slower pango instead
%configure2_5x  \
	--enable-openssl \
	--enable-ipv6 \
	--enable-threads=posix \
	--disable-xft \
	--enable-shm \
	--enable-perl \
	--enable-dbus \
	--enable-python \
	--enable-tcl=%{_libdir} \
	--disable-textfe \
	--enable-spell=libsexy \
%if %build_plf
	--enable-socks
%endif

%make

%install
%makeinstall_std

%find_lang %{name}

mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
convert xchat.png -geometry 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png
convert xchat.png -geometry 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert xchat.png -geometry 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

perl -pi -e 's,%{name}.png,%{name},g' %{buildroot}%{_datadir}/applications/xchat.desktop

desktop-file-install \
	--remove-category="Application" \
	--add-category="GTK" \
	--add-category="IRCClient" \
	--dir %{buildroot}%{_datadir}/applications \
	%{buildroot}%{_datadir}/applications/*

mkdir -p %{buildroot}%{_includedir}
cp plugins/xchat-plugin.h %{buildroot}%{_includedir}/

rm -rf %{buildroot}%{_libdir}/xchat/plugins/*.la

%preun 
%preun_uninstall_gconf_schemas apps_xchat_url_handler

%files -f xchat.lang
%doc README ChangeLog faq.html plugins/plugin20.html
%{_bindir}/xchat
%{_datadir}/applications/xchat.desktop
%{_datadir}/dbus-1/services/org.xchat.service.service
%{_datadir}/pixmaps/xchat.png
%{_iconsdir}/hicolor/*/apps/*.png
%dir %{_libdir}/xchat/plugins
%dir %{_libdir}/xchat
%{_sysconfdir}/gconf/schemas/apps_xchat_url_handler.schemas

%files devel
%{_includedir}/xchat-plugin.h

%files perl
%{_libdir}/xchat/plugins/perl.so

%files python
%{_libdir}/xchat/plugins/python.so

%files tcl
%{_libdir}/xchat/plugins/tcl.so

