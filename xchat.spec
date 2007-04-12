%define	build_plf 0

%if %{mdkversion} < 200610
%define	build_dbus 0
%else
%define	build_dbus 1
%endif

%define	build_perl 1
%define	build_python 1
%define	build_tcl 1

%{?_with_plf: %{expand: %%global build_plf 1}}

%{?_without_dbus: %{expand: %%global build_dbus 0}} 
%{?_with_dbus: %{expand: %%global build_dbus 1}} 

%{?_without_perl: %{expand: %%global build_perl 0}} 
%{?_with_perl: %{expand: %%global build_perl 1}} 

%{?_without_python: %{expand: %%global build_python 0}} 
%{?_with_python: %{expand: %%global build_python 1}} 

%{?_without_tcl: %{expand: %%global build_tcl 0}} 
%{?_with_tcl: %{expand: %%global build_tcl 1}} 


%define	name	xchat
%define	version	2.8.2
%define	rel	1
%define	main_summary	Graphical IRC client
%define	perl_version	%(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)
%define	iconname	xchat.png 

%if %build_plf
%define	distsuffix plf
%endif 

Name:		%{name}
Version:	%{version}
Release:	%mkrel %{rel}
Summary:	%{main_summary}
Group:		Networking/IRC
License:	GPL
Url:		http://www.xchat.org
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-root

Source:		http://www.xchat.org/files/source/2.6/%{name}-%{version}.tar.bz2 
Patch0:		xchat-2.6.4-ctcp_version.patch
Patch2:		xchat-2.0.8-nicksuffix.patch
Patch3:		xchat-2.6.1-servlist.patch
Patch4:		xchat-2.4.1-firefox.patch
Patch5:		xchat-latin9.patch

Obsoletes:	xchat-dbus < 2.6.8
Provides:	xchat-dbus = %version-%release

Obsoletes:	xchat-systray-integration < 2.4.6

BuildRequires:	bison
Buildrequires:	gtk+2-devel
BuildRequires:	openssl-devel
BuildRequires:	ImageMagick
BuildRequires:	GConf2
BuildRequires:	desktop-file-utils
BuildRequires:	libsexy-devel
BuildRequires:	autoconf2.5
BuildRequires:	gettext-devel
%if %build_perl
BuildRequires:	perl-devel
%endif
%if %build_python
BuildRequires:	python-devel
%endif
%if %build_tcl
BuildRequires:	tcl
%if %{mdkversion} >= 200610
BuildRequires:	tcl-devel
%endif
%endif
%if %build_dbus
BuildRequires:	dbus-glib-devel 
BuildRequires:	libtool
%endif
%if %build_plf
BuildRequires:	socks5-devel
%endif

%description
X-Chat is yet another IRC client for the X Window System, using the Gtk+
toolkit. It is pretty easy to use compared to the other Gtk+ IRC clients and
the interface is quite nicely designed.

Build Options:
--with plf       Enable SOCKS5 support (need to download from PLF)
--without dbus   Disable DBus plugin
--without perl   Disable Perl plugin 
--without python Disable Python plugin 
--without tcl    Disable TCL plugin 

%package devel
Summary:	XChat header for plugin development
Group:		Development/C

%description devel
This package contains xchat-plugin.h needed to build external plugins.

%package perl
Summary:	XChat Perl plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}
Requires:	perl-base = %perl_version

%description perl
Provides Perl scripting capability to XChat.

%package python
Summary:	XChat Python plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}

%description python
Provides Python scripting capability to XChat.

%package tcl
Summary:	XChat TCL plugin
Group:		Networking/IRC
Requires:	%{name} = %{version}

%description tcl
Provides tcl scripting capability to XChat.


%prep
%setup -q
%patch0
%patch2 -p1
%patch3 -p0 -b .default_server
%patch4 -p0 -b .firefox

%build

%if %{mdkversion} < 1010
%define	__libtoolize /bin/true
%endif

./autogen.sh

%configure2_5x  --enable-openssl \
		--enable-ipv6 \
		--enable-hebrew \
		--enable-japanese-conv \
%if %build_perl
		--enable-perl \
%else
		--disable-perl \
%endif
%if %build_dbus
		--enable-dbus \
%else
		--disable-dbus \
%endif
%if %build_python
		--enable-python \
%else
		--disable-python \
%endif
%if %build_tcl
		--enable-tcl=%{_libdir} \
%else
	        --disable-tcl
%endif
		--disable-textfe \
		--enable-spell=libsexy \
%if %build_plf
		--enable-socks
%endif

%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

%find_lang xchat

mkdir -p %{buildroot}{%{_miconsdir},%{_iconsdir},%{_liconsdir},%{_menudir}}
convert xchat.png -geometry 48x48 %{buildroot}%{_liconsdir}/%{iconname}
convert xchat.png -geometry 32x32 %{buildroot}%{_iconsdir}/%{iconname}
convert xchat.png -geometry 16x16 %{buildroot}%{_miconsdir}/%{iconname}
 
cat > $RPM_BUILD_ROOT%{_menudir}/%{name} << EOF
?package(%name): needs="x11" \
	section="Internet/Chat" \
	title="Xchat" \
	longtitle="%{main_summary}" \
	command="%{_bindir}/%{name}" \
	icon="%{name}.png" \
	xdg="true"
EOF

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="IRCClient" \
  --add-category="X-MandrivaLinux-Internet-Chat" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*

mkdir -p %{buildroot}%{_includedir}
cp plugins/xchat-plugin.h %{buildroot}%{_includedir}/

rm -rf %{buildroot}%{_libdir}/xchat/plugins/*.la

%post
%update_menus

%if %build_dbus
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/apps_xchat_url_handler.schemas > /dev/null

%preun 
if [ "$1" = "0" -a -x %{_bindir}/gconftool-2 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/apps_xchat_url_handler.schemas > /dev/null
fi
%endif

%postun
%clean_menus

%clean
rm -fr $RPM_BUILD_ROOT

%files -f xchat.lang
%defattr(-,root,root)
%doc README ChangeLog faq.html COPYING plugins/plugin20.html
%{_bindir}/xchat
%{_datadir}/applications/xchat.desktop
%{_datadir}/dbus-1/services/org.xchat.service.service
%{_datadir}/pixmaps/xchat.png
%_menudir/*
%_iconsdir/%iconname
%_liconsdir/%iconname
%_miconsdir/%iconname  
%dir %{_libdir}/xchat/plugins
%dir %{_libdir}/xchat
%{_sysconfdir}/gconf/schemas/apps_xchat_url_handler.schemas

%files devel
%defattr(-,root,root)
%{_includedir}/xchat-plugin.h

%if %build_perl
%files perl
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/perl.so
%endif

%if %build_python
%files python
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/python.so
%endif

%if %build_tcl
%files tcl
%defattr(-,root,root)
%doc README
%{_libdir}/xchat/plugins/tcl.so
%endif



