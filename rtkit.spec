Summary:	Realtime Policy and Watchdog Daemon
Name:		rtkit
Version:	0.10
Release:	1
Group:		Base
# The daemon itself is GPLv3+, the reference implementation for the client BSD
License:	GPL v3+ and BSD
URL:		http://git.0pointer.de/?p=rtkit.git
Source0:	http://0pointer.de/public/%{name}-%{version}.tar.gz
# Source0-md5:	9ab7f2a25ddf05584ea2216dfe4cefd4
BuildRequires:	dbus-devel >= 1.2
BuildRequires:	libcap-devel
BuildRequires:	polkit-devel
Requires:	dbus
Requires:	polkit
Requires:	systemd-units
Requires(post):	systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
RealtimeKit is a D-Bus system service that changes the scheduling
policy of user processes/threads to SCHED_RR (i.e. realtime scheduling
mode) on request. It is intended to be used as a secure mechanism to
allow real-time scheduling to be used by normal user processes.

%prep
%setup -q

%build
%configure \
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
if [ $1 -eq 1 ]; then
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

%files
%defattr(644,root,root,755)
%doc README LICENSE rtkit.c rtkit.h
%attr(755,root,root) %{_sbindir}/rtkitctl
%attr(755,root,root) %{_libexecdir}/rtkit-daemon
%{_datadir}/dbus-1/system-services/org.freedesktop.RealtimeKit1.service
%{_datadir}/dbus-1/interfaces/org.freedesktop.RealtimeKit1.xml
%{_datadir}/polkit-1/actions/org.freedesktop.RealtimeKit1.policy
%config(noreplace) /etc/dbus-1/system.d/org.freedesktop.RealtimeKit1.conf
%{systemdunitdir}/rtkit-daemon.service
%{_mandir}/man8/*
