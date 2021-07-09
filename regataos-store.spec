Name: regataos-store
Version: 21.2
Release: 0
Url: https://github.com/regataos/store
Summary: Application store of Regata OS
Group: System/GUI/KDE
BuildRequires: xz
BuildRequires: desktop-file-utils
BuildRequires: update-desktop-files
BuildRequires: hicolor-icon-theme
BuildRequires: -post-build-checks
%{?systemd_requires}
BuildRequires: systemd
BuildRequires: grep
License: MIT
Source1: regataos-store-%{version}.tar.xz
Requires: regataos-repo >= 5.0
Requires: xz
Requires: xdpyinfo
Requires: magma >= 5.52.2-lp152.6.1
Requires: zypper
Requires: snapd
Requires: xdg-desktop-portal
Requires: lsof
Requires: zenity
Requires: zenity-lang
Requires: pv
Requires: libnotify4
Requires: libnotify4-32bit
Requires: libnotify-tools
BuildRoot: %{_tmppath}/%{name}-%{version}-build

%description
Application store of Regata OS.

%build

%install
# Install the main store package
mkdir -p %{buildroot}/opt/regataos-base/
cp -f %{SOURCE1} %{buildroot}/opt/regataos-base/regataos-store-%{version}.tar.xz

%post
# Remove old files
if test -e /opt/regataos-store ; then
  rm -rf "/opt/regataos-store"
fi

# Extract store files at the root of the system
tar xf /opt/regataos-base/regataos-store-%{version}.tar.xz -C /

# Fix installed apps
if test -e "/tmp/regataos-store/config" ; then
	chmod 777 "/tmp/regataos-store/config"
else
	mkdir -p "/tmp/regataos-store/config"
	chmod 777 "/tmp/regataos-store/config"
fi

if test ! -e "/tmp/regataos-store/config/installed-apps.txt" ; then
	mkdir -p "/tmp/regataos-store/config"
	chmod 777 "/tmp/regataos-store/config"

    user=$(users | awk '{print $1}')
    mkdir -p "/home/$user/.config/regataos-store"
    chmod 777 "/home/$user/.config/regataos-store"
    echo "" >> "/home/$user/.config/regataos-store/installed-apps.txt"
    chmod 777 /home/$user/.config/regataos-store/*

	ln -sf "/home/$user/.config/regataos-store/installed-apps.txt" "/tmp/regataos-store/config/"
	chmod 777 /tmp/regataos-store/config/*
fi

# Create directory containing the list of installed apps
mkdir -p /opt/regataos-store/installed-apps/
chmod 777 /opt/regataos-store/installed-apps/

# Hide YaST .desktop files
if [[ $(grep -r "NoDisplay=true" "/usr/share/applications/org.opensuse.yast.Packager.desktop") != *"NoDisplay=true"* ]]; then
  echo "NoDisplay=true" >> /usr/share/applications/YaST2/org.opensuse.yast.CheckMedia.desktop
  echo "NoDisplay=true" >> /usr/share/applications/YaST2/org.opensuse.yast.SWSingle.desktop
  echo "NoDisplay=true" >> /usr/share/applications/YaST2/org.opensuse.yast.SWSource.desktop
  echo "NoDisplay=true" >> /usr/share/applications/YaST2/org.opensuse.yast.OnlineUpdate.desktop
  echo "NoDisplay=true" >> /usr/share/applications/org.opensuse.yast.Packager.desktop
fi

# Add guest user group
getent group guest-session >/dev/null || groupadd -r guest-session

# Some changes needed for the new version of Regata OS Store
if test -e "/etc/xdg/autostart/regataos-store-capture-progress-download.desktop"; then
  rm -f "/etc/xdg/autostart/regataos-store-capture-progress-download.desktop"
  rm -f "/etc/xdg/autostart/regataos-store-create-process-queues.desktop"
  rm -f "/etc/xdg/autostart/regataos-store-list-installed-apps.desktop"
  rm -f "/etc/xdg/autostart/regataos-store-run-process-queues.desktop"
  rm -f "/etc/xdg/autostart/regataos-store-snap-version-cache.desktop"
  rm -f "/etc/xdg/autostart/regataos-store-x.desktop"

  systemctl stop regataos-store-selectlanguage.service || true
  systemctl disable regataos-store-selectlanguage.service || true
  systemctl stop regataos-store-clearcache.service || true
  systemctl disable regataos-store-clearcache.service || true
  systemctl stop capture-progress-download-snap.service || true
  systemctl disable capture-progress-download-snap.service || true

  killall capture-progress-download-snap
  killall capture-progress-download
  killall snap-version-cache.sh
  killall create-process-queues
  killall run-process-queues
  killall checkapp
fi

update-desktop-database

%clean

%files
%defattr(-,root,root)
/opt/regataos-base
/opt/regataos-base/regataos-store-%{version}.tar.xz

%changelog
