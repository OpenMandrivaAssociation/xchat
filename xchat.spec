%define	build_plf 0

%if %build_plf
%define	distsuffix plf
%endif 

%{?_with_plf: %{expand: %%global build_plf 1}}

%define	perl_version %(rpm -q --qf '%%{epoch}:%%{VERSION}' perl)

Summary:	A GTK+ IRC client
Name:		xchat
Version:	2.8.8
Release:	%mkrel 8
Group:		Networking/IRC
License:	GPLv2+
Url:		http://www.xchat.org
Source0:	http://www.xchat.org/files/source/2.8/%{name}-%{version}.tar.bz2
Patch0:		xchat-2.6.4-ctcp_version.patch
Patch1:		xchat-2.0.8-nicksuffix.patch
Patch2:		xchat-2.6.1-servlist.patch
Patch3:		xchat-2.8.6-CVE-2009-0315-debian.patch
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
Buildrequires:	gtk+3-devel
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
BuildRequires:	libnotify-devel
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
%patch1 -p1
%patch2 -p0 -b .default_server
%patch3 -p1 -b .cve-2009-0315

# fedora patches
%patch100 -p0 -b .use-sysconf-to-detect-cpus
%patch101 -p1 -b .tray-icon
%patch102 -p1 -b .default-utf8
%patch103 -p1 -b .active-channel-switch
%patch104 -p0 -b .freenode-ports
%patch105 -p1 -b .libnotify07
%patch106 -p1 -b .link-against-libnotify
%patch107 -p1 -b .fixglib

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


%changelog
* Sun May 22 2011 Funda Wang <fwang@mandriva.org> 2.8.8-6mdv2011.0
+ Revision: 677089
- rebuild to add gconf2 as req

* Mon Apr 11 2011 Oden Eriksson <oeriksson@mandriva.com> 2.8.8-5
+ Revision: 652562
- sync with xchat-2.8.8-9.fc16.src.rpm

* Fri Oct 29 2010 Michael Scherer <misc@mandriva.org> 2.8.8-4mdv2011.0
+ Revision: 589983
- rebuild for python 2.7

* Sun Aug 15 2010 Funda Wang <fwang@mandriva.org> 2.8.8-3mdv2011.0
+ Revision: 569889
- rebuild for perl 5.12.1

* Thu Jul 22 2010 Jérôme Quelin <jquelin@mandriva.org> 2.8.8-2mdv2011.0
+ Revision: 556789
- perl 5.12 rebuild

* Mon Jun 21 2010 Oden Eriksson <oeriksson@mandriva.com> 2.8.8-1mdv2010.1
+ Revision: 548395
- 2.8.8
- patches 8, 9, 11, 12 are obsolete.

* Wed Apr 07 2010 Funda Wang <fwang@mandriva.org> 2.8.6-9mdv2010.1
+ Revision: 532502
- rebuild

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 2.8.6-8mdv2010.1
+ Revision: 511663
- rebuilt against openssl-0.9.8m

* Sat Oct 17 2009 Pascal Terjan <pterjan@mandriva.org> 2.8.6-7mdv2010.0
+ Revision: 458043
- Upstream fixes for 2 bugs including #54626

* Sat Aug 29 2009 Guillaume Rousse <guillomovitch@mandriva.org> 2.8.6-6mdv2010.0
+ Revision: 422289
- rebuild

* Tue Mar 03 2009 Rafael da Veiga Cabral <cabral@mandriva.com> 2.8.6-5mdv2009.1
+ Revision: 348105
- security fix for CVE-2009-0315

* Sat Dec 27 2008 Michael Scherer <misc@mandriva.org> 2.8.6-4mdv2009.1
+ Revision: 319889
- rebuild for new python
- update fuzzy patch

* Sat Dec 06 2008 Adam Williamson <awilliamson@mandriva.org> 2.8.6-3mdv2009.1
+ Revision: 310970
- rebuild for new tcl

* Sun Oct 12 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.6-2mdv2009.1
+ Revision: 292884
- drop Polish translation, which is broken and outdated (will try to provide better for upstream)
- fix compiling against latest GTK+
- Patch9: small fixes from upstream

* Sun Jun 15 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.6-1mdv2009.0
+ Revision: 219308
- drop merged upstream patches 4,5,6 and 7
- rediff patch 1
- add buildrequires on libntlm-devel
- update to new version 2.8.6

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Tue May 27 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.4-9mdv2009.0
+ Revision: 211988
- disable support for Xft(use pango by default), fixes bug with RTL languages (#41082)
- Patch8: fix crash on some systems when transparent background is enabled in xchat

* Mon May 12 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.4-8mdv2009.0
+ Revision: 206512
- add polish translation (stolen from PLD ;)
- Patch1: enable polish translation

* Mon May 12 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.4-7mdv2009.0
+ Revision: 206508
- get rid of stupid switches, like build_dbus and so forth
- enable xft and shm support
- get rid of rpath
- do not re-define name summary etc
- spec file clean

* Sun Jan 20 2008 Pascal Terjan <pterjan@mandriva.org> 2.8.4-6mdv2008.1
+ Revision: 155395
- rebuild for new perl

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Wed Dec 19 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.4-5mdv2008.1
+ Revision: 133854
- add 3 upstream patches (fixes scrollback and a mem leak)
- new license policy
- do not package COPYING file

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Sep 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.8.4-4mdv2008.0
+ Revision: 90368
- rebuild

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 2.8.4-3mdv2008.0
+ Revision: 82091
- remove extension from icon file name
- rebuild for new soname of tcl

* Tue Aug 28 2007 Pascal Terjan <pterjan@mandriva.org> 2.8.4-2mdv2008.0
+ Revision: 72749
- Require libnotify to get the balloon alerts working

* Wed Jul 04 2007 Pascal Terjan <pterjan@mandriva.org> 2.8.4-1mdv2008.0
+ Revision: 47879
- 2.8.4
- drop latin9 patch, no time to work on it

* Fri Jun 22 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 2.8.2-3mdv2008.0
+ Revision: 42663
- add missing macros
- rebuild
- drop old menu stule
- drop X-Mandriva
- move icons to the fd.o directory


* Wed Apr 04 2007 Pascal Terjan <pterjan@mandriva.org> 2.8.2-1mdv2007.1
+ Revision: 150658
- Disable p5 for now, it's really broken
- 2.8.2
- Update p5
- Drop p6

* Sat Mar 10 2007 Pascal Terjan <pterjan@mandriva.org> 2.8.0-2mdv2007.1
+ Revision: 140571
- bump release
- Use autogen.sh to update po/ for new gettext

  + Frederic Crozat <fcrozat@mandriva.com>
    -Fix .desktop file category
    -Obsolete xchat-systray-integration

* Fri Jan 05 2007 Pascal Terjan <pterjan@mandriva.org> 2.8.0-1mdv2007.1
+ Revision: 104546
- 2.8.0
- add upstream patch fixing /back
- add a patch to provide ISO-8859-15/UTF-8 hybrid charset

* Tue Dec 12 2006 Michael Scherer <misc@mandriva.org> 2.6.8-2mdv2007.1
+ Revision: 95301
- Rebuild for new python

* Wed Oct 18 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.8-1mdv2007.0
+ Revision: 65946
- BuildRequires dbus-glib-devel instead of dbus-devel
- BuildRequires gettext-devel
- 2.6.8
- DBUS plugin is no longer a plugin
- Import xchat

* Sat Aug 12 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.6-3mdv2007.0
- Fix crash in filechoser when dbus plugin loaded (P5)

* Wed Aug 02 2006 Frederic Crozat <fcrozat@mandriva.com> 2.6.6-2mdv2007.0
- Rebuild with latest dbus

* Wed Jul 19 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.6-1mdv2007.0
- New release 2.6.6
- Drop P5
- Use libsexy for spellchecking

* Tue Jul 04 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.4-3mdv2007.0
- Fix group of -devel subpackage
- Escape %% in changelog

* Tue Jul 04 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.4-2mdv2007.0
- Remove invalid category from desktop file

* Fri Jun 09 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.4-1mdv2007.0
- New release 2.6.4
- Fix source URL
- Add upstream patch to fix proxy (P5)
- Updated P0

* Sun May 07 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.2-3mdk
- BuildRequires desktop-file-utils

* Fri May 05 2006 Frederic Crozat <fcrozat@mandriva.com> 2.6.2-2mdk
- Add categories to desktop file
- fix preun script

* Tue Mar 28 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.2-1mdk
- 2.6.2
- don't ship .la from plugins

* Fri Jan 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.6.1-4mdk
- Rebuild with latest dbus

* Mon Jan 23 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.1-3mdk
- rebuild for new perl

* Tue Jan 10 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.1-2mdk
- Ease backports

* Sat Jan 07 2006 Pascal Terjan <pterjan@mandriva.org> 2.6.1-1mdk
- 2.6.1
- Drop Patch5 (fixed upstream)
- Drop xchat-text, broken again. Nobody should really miss it.
- Update Patch3

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.6.0-7mdk
- rebuilt to pickup new tcl lib

* Mon Nov 14 2005 Oden Eriksson <oeriksson@mandriva.com> 2.6.0-6mdk
- rebuilt against openssl-0.9.8a

* Mon Nov 07 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.6.0-5mdk
- add BuildRequires: libtool (for dbus plugin) GConf2

* Sat Nov 05 2005 Michael Scherer <misc@mandriva.org> 2.6.0-4mdk
- fix %%post script ( error when registering the handler ), thanks yanntech
- complete --with/--without

* Fri Nov 04 2005 Pascal Terjan <pterjan@mandriva.org> 2.6.0-3mdk
- add new options to the description

* Thu Nov 03 2005 Michael Scherer <misc@mandriva.org> 2.6.0-2mdk
- add mkrel
- add with and without option for perl/python/dbus/tcl
- place xchat-remote and the schema in the dbus package

* Thu Nov 03 2005 Pascal Terjan <pterjan@mandriva.org> 2.6.0-1mdk
- 2.6.0
- Drop patch5
- New Patch5 (fix fe-text building)
- New subpackage for dbus plugin
- Install gconf schemas

* Sat Sep 24 2005 Eskild Hustvedt <eskild@mandriva.org> 2.4.5-2mdk
- Fixed menu (bug #18808)

* Mon Sep 12 2005 Pascal Terjan <pterjan@mandriva.org> 2.4.5-1mdk
- 2.4.5
- patch5 from upstream fixing a crash
- Updated patch3

* Wed Jun 22 2005 Pascal Terjan <pterjan@mandriva.org> 2.4.4-1mdk
- 2.4.4
- become rpmbuildupdate aware

* Wed Jun 08 2005 Marcel Pol <mpol@mandriva.org> 2.4.3-4mdk
- update P3: s/mandrake/mandriva

* Fri May 20 2005 Pascal Terjan <pterjan@mandriva.org> 2.4.3-3mdk
- Rebuild for new perl

* Wed May 11 2005 Pascal Terjan <pterjan@mandriva.org> 2.4.3-2mdk
- Don't require specific version of python/tcl as the correct lib is already
  required. For perl we only require libperl.so so we really need to specify
  the version.

* Sun Apr 03 2005 Pascal Terjan <pterjan@mandrake.org> 2.4.3-1mdk
- 2.4.3

* Sun Mar 20 2005 Pascal Terjan <pterjan@mandrake.org> 2.4.2-1mdk
- 2.4.2
- Drop patch6

* Sat Jan 15 2005 Pascal Terjan <pterjan@mandrake.org> 2.4.1-4mdk
- fix P4

* Sat Dec 04 2004 Pascal Terjan <pterjan@mandrake.org> 2.4.1-3mdk
- really rebuild for new python...

* Sat Dec 04 2004 Pascal Terjan <pterjan@mandrake.org> 2.4.1-2mdk
- rebuild for new python

* Tue Nov 23 2004 Pascal Terjan <pterjan@mandrake.org> 2.4.1-1mdk
- 2.4.1
- fix URL handler for firefox (P4)
- fix xchat-text build (P5 from CVS)

* Mon Nov 15 2004 Pascal Terjan <pterjan@mandrake.org> 2.4.0-3mdk
- rebuild for new perl

* Tue Sep 07 2004 Marcel Pol <mpol@mandrake.org> 2.4.0-2mdk
- patch3, default server/channel set to FreeNode/#mandrake

* Tue Aug 17 2004 Pascal Terjan <pterjan@mandrake.org> 2.4.0-1mdk
- 2.4.0
- Drop patches 3 and 4

* Thu Aug 05 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.10-3mdk
- New version of Patch4

* Tue Jul 27 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.10-2mdk
- Package xchat-plugin.h in a -devel

* Wed Jul 14 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.10-1mdk
- 2.0.10
- Official patches for focus and completion (P3 and P4)
- Drop P1 (old completion no longer exists)

* Fri Jul 09 2004 Rafael Garcia-Suarez <rgarciasuarez@mandrakesoft.com> 2.0.9-3mdk
- Rebuild for new perl

* Fri Jun 11 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.9-2mdk
- Rebuild for new python

* Sun Jun 06 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.9-1mdk
- 2.0.9
- Drop patch3

* Wed Apr 28 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.8-5mdk
- Apply patch to fix socks5 (only used in plf...)

* Wed Apr 21 2004 Pascal Terjan <pterjan@mandrake.org> 2.0.8-4mdk
- Add Patch2 to keep : as nick separator after completion
  (patch from Sunny Dubey <sunny@opencurve.org>)

* Wed Apr 07 2004 Michael Scherer <misc@mandrake.org> 2.0.8-3mdk 
- rebuild for new perl

