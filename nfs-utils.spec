Summary: NFS utlilities and supporting daemons for the kernel NFS server.
Name: nfs-utils
Version: 0.3.1
Release: 6.71
Source0: ftp://nfs.sourceforge.net/pub/nfs/nfs-utils-%{version}.tar.gz
Source1: ftp://nfs.sourceforge.net/pub/nfs/nfs.doc.tar.gz
Source10: nfs.init
Source11: nfslock.init
Patch0: nfs-utils-0.3.1-drop-privs.patch
Patch1: nfs-utils-0.2beta-nowrap.patch
Patch2: no-chroot.patch
Patch3: nfs-utils-0.3.1-statd-manpage.patch
Patch4: eepro-support.patch
Patch5: time-h.patch
Patch6: syslog-level.patch
Patch7: nfs-utils-1.0.3-mountd.secfix.patch
Group: System Environment/Daemons
Obsoletes: nfs-server
Obsoletes: knfsd
Obsoletes: knfsd-clients
Obsoletes: nfs-server-clients 
Obsoletes: knfsd-lock
Provides: nfs-server 
Provides: nfs-server-clients 
Provides: knfsd-lock 
Provides: knfsd-clients 
Provides: knfsd
License: GPL
Buildroot: %{_tmppath}/%{name}-root
Requires: kernel >= 2.2.14, portmap >= 4.0, sed, gawk
Prereq: /sbin/chkconfig /usr/sbin/useradd

%description
The nfs-utils package provides a daemon for the kernel NFS server and
related tools, which provides a much higher level of performance than the
traditional Linux NFS server used by most users.

This package also contains the showmount program.  Showmount queries the
mount daemon on a remote host for information about the NFS (Network File
System) server on the remote host.  For example, showmount can display the
clients which are mounted on that host.

%prep
%setup -q -a 1 
%patch -p1 -b .drop-privs
%patch1 -p0
%patch2 -p1 -b .no-chroot
%patch3 -p1 -b .statd-manpage
%patch4 -p1 -b .eepro-support
%patch5 -p1 -b .time-h
%patch6 -p1 -b .syslog-level
%patch7 -p1 -b .secfix

%build
#
# Hack to enable netgroups.  If anybody knows the right way to do
# this, please help yourself.
#
ac_cv_func_innetgr=yes \
CFLAGS="$RPM_OPT_FLAGS" ./configure --mandir=${RPM_BUILD_ROOT}%{_mandir}
make all

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{/sbin,/usr/sbin}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/{man5,man8}
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
make install install_prefix=$RPM_BUILD_ROOT
install -s -m 755 tools/rpcdebug/rpcdebug $RPM_BUILD_ROOT/sbin
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT/etc/rc.d/init.d/nfs
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT/etc/rc.d/init.d/nfslock
touch $RPM_BUILD_ROOT/var/lib/nfs/rmtab
mv $RPM_BUILD_ROOT/usr/sbin/{rpc.lockd,rpc.statd} $RPM_BUILD_ROOT/sbin

mkdir -p $RPM_BUILD_ROOT/var/lib/nfs/statd

# we are using quotad from quota utils
rm %{buildroot}/%{_mandir}/man8/rquotad*
rm %{buildroot}/%{_sbindir}/rpc.rquotad

%clean
rm -rf $RPM_BUILD_ROOT

%pre
/usr/sbin/useradd -c "RPC Service User" -r \
        -s /bin/false -u 29 -d /var/lib/nfs rpcuser 2>/dev/null || :

%post
/sbin/chkconfig --add nfs
/sbin/chkconfig --add nfslock

%preun
if [ "$1" = "0" ]; then
    /sbin/chkconfig --del nfs
    /sbin/chkconfig --del nfslock
    /usr/sbin/userdel rpcuser 2>/dev/null || :
    /usr/sbin/groupdel rpcuser 2>/dev/null || :
fi

%triggerpostun -- nfs-server
/sbin/chkconfig --add nfs

%triggerpostun -- knfsd
/sbin/chkconfig --add nfs

%triggerpostun -- knfsd-clients
/sbin/chkconfig --add nfslock

%files
%defattr(-,root,root)
%config /etc/rc.d/init.d/nfs
%dir /var/lib/nfs
%dir %attr(700,rpcuser,rpcuser) /var/lib/nfs/statd
%config(noreplace) /var/lib/nfs/xtab
%config(noreplace) /var/lib/nfs/etab
%config(noreplace) /var/lib/nfs/rmtab
%doc nfs/*.html nfs/*.ps linux-nfs/*
/sbin/rpcdebug
/sbin/rpc.lockd
/sbin/rpc.statd
/usr/sbin/exportfs
/usr/sbin/nfsstat
/usr/sbin/nhfsstone
/usr/sbin/rpc.mountd
/usr/sbin/rpc.nfsd
/usr/sbin/showmount
%{_mandir}/*/*
%config /etc/rc.d/init.d/nfslock

%changelog
* Tue Apr 10 2001 Michael K. Johnson <johnsonm@redhat.com>
- do not start lockd on kernel 2.2.18 or higher (done automatically)

* Fri Mar 30 2001 Preston Brown <pbrown@redhat.com>
- don't use rquotad from here now; quota package contains a version that 
  works with 2.4 (#33738)

* Tue Mar 12 2001 Bob Matthews <bmatthews@redhat.com>
- Statd logs at LOG_DAEMON rather than LOG_LOCAL5
- s/nfs/\$0/ where appropriate in init scripts

* Tue Mar  6 2001 Jeff Johnson <jbj@redhat.com>
- Move to nfs-utils-0.3.1

* Wed Feb 14 2001 Bob Matthews <bmatthews@redhat.com>
- #include <time.h> patch

* Mon Feb 12 2001 Bob Matthews <bmatthews@redhat.com>
- Really enable netgroups

* Mon Feb  5 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- i18nize initscripts

* Fri Jan 19 2001 Bob Matthews <bmatthews@redhat.com>
- Increased {s,r}blen in rpcmisc.c:makesock to accommodate eepro100

* Tue Jan 16 2001 Bob Matthews <bmatthews@redhat.com>
- Hackish fix in build section to enable netgroups

* Wed Jan  3 2001 Bob Matthews <bmatthews@redhat.com>
- Fix incorrect file specifications in statd manpage.
- Require gawk 'cause it's used in nfslock init script.

* Thu Dec 13 2000 Bob Matthews <bmatthews@redhat.com>
- Require sed because it's used in nfs init script

* Tue Dec 12 2000 Bob Matthews <bmatthews@redhat.com>
- Don't do a chroot(2) after dropping privs, in statd.

* Mon Dec 11 2000 Bob Matthews <bmatthews@redhat.com>
- NFSv3 if kernel >= 2.2.18, detected in init script

* Thu Nov 23 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 0.2.1

* Tue Nov 14 2000 Bill Nottingham <notting@redhat.com>
- don't start lockd on 2.4 kernels; it's unnecessary

* Tue Sep  5 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- more portable fix for mandir

* Sun Sep  3 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 0.2-release

* Fri Sep  1 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- fix reload script

* Thu Aug 31 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- update to 0.2 from CVS
- adjust statd-drop-privs patch
- disable tcp_wrapper support

* Wed Aug  2 2000 Bill Nottingham <notting@redhat.com>
- fix stop priority of nfslock

* Tue Aug  1 2000 Bill Nottingham <notting@redhat.com>
- um, actually *include and apply* the statd-drop-privs patch

* Mon Jul 24 2000 Bill Nottingham <notting@redhat.com>
- fix init script ordering (#14502)

* Sat Jul 22 2000 Bill Nottingham <notting@redhat.com>
- run statd chrooted and as non-root
- add prereqs

* Tue Jul 18 2000 Trond Eivind Glomsrød <teg@redhat.com>
- use "License", not "Copyright"
- use %%{_tmppath} and %%{_mandir}

* Mon Jul 17 2000 Matt Wilson <msw@redhat.com>
- built for next release

* Mon Jul 17 2000 Matt Wilson <msw@redhat.com>
- 0.1.9.1
- remove patch0, has been integrated upstream

* Wed Feb  9 2000 Bill Nottingham <notting@redhat.com>
- the wonderful thing about triggers, is triggers are wonderful things...

* Thu Feb 03 2000 Cristian Gafton <gafton@redhat.com>
- switch to nfs-utils as the base tree
- fix the statfs patch for the new code base
- single package that obsoletes everything we had before (if I am to keep
  some traces of my sanity with me...)

* Mon Jan 17 2000 Preston Brown <pbrown@redhat.com>
- use statfs syscall instead of stat to determinal optimal blksize
