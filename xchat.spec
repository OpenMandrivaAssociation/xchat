%define	build_plf 0

%if %build_plf
%define	distsuffix plf
%endif 

%{?_with_plf: %{expand: %%global build_plf 1}}

%define	perl_version %(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)

Summary:	A GTK+ IRC client
Name:		xchat
Version:	2.8.6
Release:	%mkrel 9
Group:		Networking/IRC
License:	GPLv2+
Url:		http://www.xchat.org
Source0:	http://www.xchat.org/files/source/2.8/%{name}-%{version}.tar.bz2
Patch0:		xchat-2.6.4-ctcp_version.patch
Patch2:		xchat-2.0.8-nicksuffix.patch
Patch3:		xchat-2.6.1-servlist.patch
# (tpg) https://bugzilla.redhat.com/show_bug.cgi?id=282691
Patch8:		xchat-2.8.4-shm-pixmaps.patch
Patch9:		http://xchat.org/files/source/2.8/patches/xc286-smallfixes.diff
Patch10:        xchat-2.8.6-CVE-2009-0315-debian.patch 
Patch11:	xchat-2.8.6-C_onnect.patch
Patch12:	xchat-2.8.6-save-favorites.patch
BuildRequires:	bison
Buildrequires:	gtk+2-devel
BuildRequires:	openssl-devel
BuildRequires:	imagemagick
BuildRequires:	GConf2
BuildRequires:	desktop-file-utils
BuildRequires:	libsexy-devel
BuildRequires:	gettext-devel
BuildRequires:	perl-devel
BuildRequires:	python-devel
BuildRequires:	tcl
BuildRequires:	tcl-devel
BuildRequires:	dbus-glib-devel
BuildRequires:	libntlm-devel
%if %build_plf
BuildRequires:	socks5-devel
%endif
Obsoletes:	xchat-dbus < 2.6.8
Provides:	xchat-dbus = %{version}-%{release}
Obsoletes:	xchat-systray-integration < 2.4.6
# To get the balloon alerts working
Requires:	libnotify
Buildroot:	%{_tmppath}/%{name}-%{version}-buildroot

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
%patch2 -p1
%patch3 -p0 -b .default_server
%patch8 -p1
%patch9 -p1
%patch10 -p1 -b .cve-2009-0315
%patch11 -p0 -b .C_onnect
%patch12 -p0 -b .favorites
%build
# fix build against latest GTK+
sed -i -e 's/#define GTK_DISABLE_DEPRECATED//g' src/fe-gtk/*.c

./autogen.sh
# (tpg) disable Xft as it breaks RTL languages
# use slower pango instead

%configure2_5x  \
	--enable-openssl \
	--enable-ipv6 \
	--disable-rpath \
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
rm -rf %{buildroot}
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
  --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

mkdir -p %{buildroot}%{_includedir}
cp plugins/xchat-plugin.h %{buildroot}%{_includedir}/

rm -rf %{buildroot}%{_libdir}/xchat/plugins/*.la

%if %mdkversion < 200900
%post
%{update_menus}
%update_icon_cache hicolor
%post_install_gconf_schemas apps_xchat_url_handler
%endif

%preun 
%preun_uninstall_gconf_schemas apps_xchat_url_handler

%if %mdkversion < 200900
%postun
%{clean_menus}
%clean_icon_cache hicolor
%endif

%clean
rm -fr %{buildroot}

%files -f xchat.lang
%defattr(-,root,root)
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
%defattr(-,root,root)
%{_includedir}/xchat-plugin.h

%files perl
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/perl.so

%files python
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/python.so

%files tcl
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/tcl.so
