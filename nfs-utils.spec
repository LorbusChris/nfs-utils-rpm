Summary: NFS utlilities and supporting daemons for the kernel NFS server.
Name: nfs-utils
Version: 0.1.9.1
Release: 7
Source0: ftp://nfs.sourceforge.net/pub/nfs/nfs-utils-0.1.9.1.tar.gz
Source1: ftp://nfs.sourceforge.net/pub/nfs/nfs.doc.tar.gz
Source10: nfs.init
Source11: nfslock.init
Patch: statd-drop-privs.patch
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
Requires: kernel >= 2.2.14, portmap >= 4.0
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

%build
CFLAGS="$RPM_OPT_FLAGS" ./configure
make all

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT{/sbin,/usr/{sbin,man/man5,man/man8,share/man/man5,share/man/man8}}
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d
make install install_prefix=$RPM_BUILD_ROOT
install -s -m 755 tools/rpcdebug/rpcdebug $RPM_BUILD_ROOT/sbin
install -m 755 %{SOURCE10} $RPM_BUILD_ROOT/etc/rc.d/init.d/nfs
install -m 755 %{SOURCE11} $RPM_BUILD_ROOT/etc/rc.d/init.d/nfslock
touch $RPM_BUILD_ROOT/var/lib/nfs/rmtab
mv $RPM_BUILD_ROOT/usr/sbin/{rpc.lockd,rpc.statd} $RPM_BUILD_ROOT/sbin
mv $RPM_BUILD_ROOT/usr/man/man5/* $RPM_BUILD_ROOT/usr/share/man/man5/
mv $RPM_BUILD_ROOT/usr/man/man8/* $RPM_BUILD_ROOT/usr/share/man/man8/

mkdir -p $RPM_BUILD_ROOT/var/lib/nfs/statd

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
/usr/sbin/rpc.rquotad
/usr/sbin/showmount
%{_mandir}/*/*
%config /etc/rc.d/init.d/nfslock

%changelog
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
