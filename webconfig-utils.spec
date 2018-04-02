%define enginedir /usr/clearos/sandbox/

Name: webconfig-utils
Version: 7.4.1
Release: 1%dist
Group: Applications/System
Summary: Tools from the webconfig API framework
Source: %{name}-%{version}.tar.gz
License: GPL
Requires: webconfig-php
Requires: util-linux
Requires: system-base >= 7.4.2
BuildRequires: webconfig-php-devel
BuildRequires: pam-devel

%description
Framework tools and libraries

%prep
%setup -q
%build
rm -rf $RPM_BUILD_ROOT

cd php-ifconfig
%configure \
	--prefix=%{enginedir} \
	--with-php-config=%{enginedir}%{_bindir}/php-config \
	--enable-ifconfig
make

cd ../php-statvfs
%configure \
	--prefix=%{enginedir} \
	--with-php-config=%{enginedir}%{_bindir}/php-config \
	--enable-statvfs
make

cd ../utils
gcc -O2 app-rename.c -o app-rename
gcc -O2 app-passwd.c -o app-passwd -l pam
gcc -O2 app-realpath.c -o app-realpath

%install
mkdir -p -m 755 $RPM_BUILD_ROOT%{enginedir}%{_libdir}/php/modules
mkdir -p -m 755 $RPM_BUILD_ROOT%{enginedir}%{_sysconfdir}/php.d
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sbindir}
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.d
mkdir -p -m 755 $RPM_BUILD_ROOT/etc/clearos
mkdir -p -m 755 $RPM_BUILD_ROOT/usr/clearos
mkdir -p -m 755 $RPM_BUILD_ROOT/usr/clearos/bin
mkdir -p -m 755 $RPM_BUILD_ROOT/var/clearos

# ifconfig PHP module
cp php-ifconfig/modules/ifconfig.so $RPM_BUILD_ROOT%{enginedir}%{_libdir}/php/modules
echo "extension=ifconfig.so" > $RPM_BUILD_ROOT%{enginedir}%{_sysconfdir}/php.d/ifconfig.ini

# statvfs PHP module
cp php-statvfs/modules/statvfs.so $RPM_BUILD_ROOT%{enginedir}%{_libdir}/php/modules
echo "extension=statvfs.so" > $RPM_BUILD_ROOT%{enginedir}%{_sysconfdir}/php.d/statvfs.ini

# Helper tools
install -m 755 utils/app-passwd $RPM_BUILD_ROOT%{_sbindir}
install -m 755 utils/app-rename $RPM_BUILD_ROOT%{_sbindir}
install -m 755 utils/app-realpath $RPM_BUILD_ROOT%{_sbindir}

# Sudoers
install -m 0640 framework-utils-sudoers $RPM_BUILD_ROOT%{_sysconfdir}/sudoers.d/framework-utils

%post
CHECKSUDO=`grep '^Defaults:webconfig' /etc/sudoers 2>/dev/null`
if [ -n "$CHECKSUDO" ]; then
    logger -p local6.notice -t installer "webconfig-utils - migrating syslog policy"
    sed -i -e '/Defaults:webconfig/d' /etc/sudoers
fi

%files
%defattr(-,root,root)
%dir /etc/clearos
%dir /usr/clearos
%dir /usr/clearos/bin
%dir /var/clearos
%{enginedir}%{_libdir}/php/modules/ifconfig.so
%{enginedir}%{_libdir}/php/modules/statvfs.so
%{enginedir}%{_sysconfdir}/php.d/ifconfig.ini
%{enginedir}%{_sysconfdir}/php.d/statvfs.ini
%{_sbindir}/app-passwd
%{_sbindir}/app-rename
%{_sbindir}/app-realpath
%attr(0640,root,root) %{_sysconfdir}/sudoers.d/framework-utils
