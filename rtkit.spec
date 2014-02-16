Summary:	Realtime Policy and Watchdog Daemon
Summary(pl.UTF-8):	Demon polityki i dozorujący dla szeregowania czasu rzeczywistego (RealTime)
Name:		rtkit
Version:	0.11
Release:	1
Group:		Base
# The daemon itself is GPLv3+, the reference implementation for the client BSD
License:	GPL v3+ (daemon), BSD (client library)
Source0:	http://0pointer.de/public/%{name}-%{version}.tar.xz
# Source0-md5:	a96c33b9827de66033d2311f82d79a5d
URL:		http://git.0pointer.de/?p=rtkit.git
BuildRequires:	dbus-devel >= 1.2
BuildRequires:	libcap-devel
BuildRequires:	polkit-devel
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post):	systemd-units
Requires(preun):	systemd-units
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(postun):	systemd-units
Requires:	dbus
Requires:	polkit
Requires:	systemd-units
Provides:	group(rtkit)
Provides:	user(rtkit)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
RealtimeKit is a D-Bus system service that changes the scheduling
policy of user processes/threads to SCHED_RR (i.e. realtime scheduling
mode) on request. It is intended to be used as a secure mechanism to
allow real-time scheduling to be used by normal user processes.

%description -l pl.UTF-8
RealtimeKit to usługa systemowa D-Bus zmieniająca na żądanie politykę
szeregowania procesów/wątków użytkownika na SCHED_RR (tj. tryb
szeregowania czasu rzeczywistego). Jest zaprojektowana jako bezpieczny
mechanizm pozwalający na wykorzystywanie szeregowania czasu
rzeczywistego przez procesy zwykłych użytkowników.

%prep
%setup -q

%build
%configure \
	--disable-silent-rules \
	--with-systemdsystemunitdir=%{systemdunitdir} \

%{__make}

./rtkit-daemon --introspect > org.freedesktop.RealtimeKit1.xml

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -Dp org.freedesktop.RealtimeKit1.xml $RPM_BUILD_ROOT%{_datadir}/dbus-1/interfaces/org.freedesktop.RealtimeKit1.xml

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 278 rtkit
%useradd -r -u 278 -g rtkit -d /proc -s /sbin/nologin -c "RealtimeKit" rtkit

%post
if [ "$1" -eq 1 ]; then
	/bin/systemctl enable rtkit.service >/dev/null 2>&1 || :
fi
dbus-send --system --type=method_call --dest=org.freedesktop.DBus / org.freedesktop.DBus.ReloadConfig >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ]; then
	/bin/systemctl --no-reload disable rtkit-daemon.service >/dev/null 2>&1 || :
	/bin/systemctl stop rtkit-daemon.service >/dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ "$1" = "0" ]; then
	%userremove rtkit
	%groupremove rtkit
fi

%files
%defattr(644,root,root,755)
%doc README LICENSE rtkit.c rtkit.h
%attr(755,root,root) %{_sbindir}/rtkitctl
%attr(755,root,root) %{_libexecdir}/rtkit-daemon
%{_datadir}/dbus-1/interfaces/org.freedesktop.RealtimeKit1.xml
%{_datadir}/dbus-1/system-services/org.freedesktop.RealtimeKit1.service
%{_datadir}/polkit-1/actions/org.freedesktop.RealtimeKit1.policy
%config(noreplace) /etc/dbus-1/system.d/org.freedesktop.RealtimeKit1.conf
%{systemdunitdir}/rtkit-daemon.service
%{_mandir}/man8/rtkitctl.8*
