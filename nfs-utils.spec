Summary: NFS utlilities and supporting daemons for the kernel NFS server.
Name: nfs-utils
Version: 1.0.7
Release: 5

# group all 32bit related archs
%define all_32bit_archs i386 i686 athlon

Source0: http://unc.dl.sourceforge.net/sourceforge/nfs/nfs-utils-1.0.7.tar.gz
Source1: ftp://nfs.sourceforge.net/pub/nfs/nfs.doc.tar.gz

%define idmapvers 0.10
Source2: http://www.citi.umich.edu/projects/nfsv4/linux/libnfsidmap/nfsidmap-%{idmapvers}.tar.gz
%define eventvers 1.0b
Source3: http://monkey.org/~provos/libevent-%{eventvers}.tar.gz

Source10: nfs.init
Source11: nfslock.init
Source12: rpcidmapd.init
Source13: rpcgssd.init
Source14: rpcsvcgssd.init

#
# CITI NFS4 Patches
#
Patch20: nfs-utils-1.0.6-citi-mountd_flavors.patch

#
# Local Patches
#
Patch50: nfs-utils-1.0.5-statdpath.patch
Patch51: nfs-utils-1.0.6-zerostats.patch
Patch52: nfs-utils-1.0.6-mountd.patch
Patch53: nfs-utils-1.0.6-expwarn.patch
Patch54: nfs-utils-1.0.7-sgi-statd-fixes.patch
Patch55: nfs-utils-1.0.6-fd-sig-cleanup.patch
Patch56: nfs-utils-1.0.6-idmap-syslog.patch
Patch57: nfs-utils-1.0.6-idmap.conf.patch
Patch58: nfs-utils-1.0.6-rquotad-overflow.patch
Patch59: nfs-utils-1.0.6-statd-notify-hostname.patch
Patch60: nfs-utils-1.0.7-rpcsecgss-debug.patch
Patch61: nfs-utils-1.0.7-xlog-loginfo.patch

Patch100: nfs-utils-1.0.7-compile.patch
Patch150: nfs-utils-1.0.6-pie.patch

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
Requires: kernel >= 2.2.14, portmap >= 4.0, sed, gawk, sh-utils, fileutils, textutils, grep
Requires: modutils >= 2.4.26-9
BuildRequires: krb5-devel >= 1.3.1 autoconf >= 2.57 openldap-devel >= 2.2
Prereq: /sbin/chkconfig /usr/sbin/useradd /sbin/nologin

%description
The nfs-utils package provides a daemon for the kernel NFS server and
related tools, which provides a much higher level of performance than the
traditional Linux NFS server used by most users.

This package also contains the showmount program.  Showmount queries the
mount daemon on a remote host for information about the NFS (Network File
System) server on the remote host.  For example, showmount can display the
clients which are mounted on that host.

%prep
%setup -q -a1 -a2 -a3
#
# Set up the support libs
#
mv nfsidmap-%{idmapvers} support/nfsidmap
mv libevent-%{eventvers} support/event

%patch20 -p1 

%patch50 -p1 -b .statdpath
%patch51 -p1 -b .zerostats
%patch52 -p1 -b .mountd
%patch53 -p1 -b .expwarn
%patch54 -p1 -b .sgi
%patch55 -p1 -b .cleanup
%patch56 -p1 -b .syslog
%patch57 -p1 -b .conf
%patch58 -p1 -b .overflow
%patch59 -p1 -b .notify
%patch60 -p1 -b .rpcsecgss
%patch61 -p1 -b .xlog


# Do the magic to get things to compile
%patch100 -p1 -b .compile
%patch150 -p1 -b .pie
%ifarch s390 s390x
perl -pi -e 's/-fpie/-fPIE/' */*/Makefile
%endif

# Remove .orig files
find . -name "*.orig" | xargs rm -f

%build

autoconf

#
# Hack to enable netgroups.  If anybody knows the right way to do
# this, please help yourself.
#
ac_cv_func_innetgr=yes \
	CFLAGS="$RPM_OPT_FLAGS" %configure --enable-secure-statd

cd support/nfsidmap; %configure --prefix=$RPM_BUILD_ROOT
cd ../../support/event; %configure --prefix=$RPM_BUILD_ROOT
cd ../../

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
install -m 755 %{SOURCE12} $RPM_BUILD_ROOT/etc/rc.d/init.d/rpcidmapd
install -m 755 %{SOURCE13} $RPM_BUILD_ROOT/etc/rc.d/init.d/rpcgssd
install -m 755 %{SOURCE14} $RPM_BUILD_ROOT/etc/rc.d/init.d/rpcsvcgssd

install -m 644 utils/idmapd/idmapd.conf \
	$RPM_BUILD_ROOT/etc/idmapd.conf
install -m 644 support/gssapi/SAMPLE_gssapi_mech.conf \
	$RPM_BUILD_ROOT/etc/gssapi_mech.conf

mkdir -p $RPM_BUILD_ROOT/var/lib/nfs/rpc_pipefs

touch $RPM_BUILD_ROOT/var/lib/nfs/rmtab
mv $RPM_BUILD_ROOT/usr/sbin/{rpc.lockd,rpc.statd} $RPM_BUILD_ROOT/sbin

mkdir -p $RPM_BUILD_ROOT/var/lib/nfs/statd

# we are using quotad from quota utils
rm %{buildroot}/%{_mandir}/man8/rquotad*
rm %{buildroot}/%{_mandir}/man8/rpc.rquotad*
rm %{buildroot}/%{_sbindir}/rpc.rquotad

%clean
rm -rf $RPM_BUILD_ROOT

%pre
/usr/sbin/useradd -c "RPC Service User" -r \
        -s /sbin/nologin -u 29 -d /var/lib/nfs rpcuser 2>/dev/null || :
# Define the correct unsigned uid value for 32 or 64 bit archs
%ifarch %{all_32bit_archs}
%define nfsnobody_uid   65534
%else
%define nfsnobody_uid   4294967294
%endif

# If UID 65534 (or 4294967294 64bit archs) is unassigned, create user "nfsnobody"
cat /etc/passwd | cut -d':' -f 3 | grep --quiet %{nfsnobody_uid} 2>/dev/null
if [ "$?" -eq 1 ]; then
	/usr/sbin/useradd -c "Anonymous NFS User" -r \
		-s /sbin/nologin -u %{nfsnobody_uid} -d /var/lib/nfs nfsnobody 2>/dev/null || :
fi

%post
/sbin/chkconfig --add nfs
/sbin/chkconfig --add nfslock
/sbin/chkconfig --add rpcidmapd
/sbin/chkconfig --add rpcgssd
/sbin/chkconfig --add rpcsvcgssd

%preun
if [ "$1" = "0" ]; then
    /etc/rc.d/init.d/nfs stop
	/etc/rc.d/init.d/rpcgssd stop
	/etc/rc.d/init.d/rpcidmapd stop
    /etc/rc.d/init.d/nfslock stop
    /sbin/chkconfig --del rpcidmapd
    /sbin/chkconfig --del rpcgssd
    /sbin/chkconfig --del rpcsvcgssd
    /sbin/chkconfig --del nfs
    /sbin/chkconfig --del nfslock
    /usr/sbin/userdel rpcuser 2>/dev/null || :
    /usr/sbin/groupdel rpcuser 2>/dev/null || :
    /usr/sbin/userdel nfsnobody 2>/dev/null || :
fi

%postun
if [ "$1" -ge 1 ]; then
	/etc/rc.d/init.d/rpcidmapd condrestart > /dev/null
	/etc/rc.d/init.d/rpcgssd condrestart > /dev/null
	/etc/rc.d/init.d/nfs condrestart > /dev/null
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
%config /etc/rc.d/init.d/rpcidmapd
%config /etc/rc.d/init.d/rpcgssd
%config /etc/rc.d/init.d/rpcsvcgssd
%config(noreplace) /etc/idmapd.conf
%config(noreplace) /etc/gssapi_mech.conf
%dir /var/lib/nfs/rpc_pipefs
%dir /var/lib/nfs
%dir %attr(700,rpcuser,rpcuser) /var/lib/nfs/statd
%config(noreplace) /var/lib/nfs/xtab
%config(noreplace) /var/lib/nfs/etab
%config(noreplace) /var/lib/nfs/rmtab
%config(noreplace) /var/lib/nfs/state
%doc nfs/*.html nfs/*.ps linux-nfs/*
/sbin/rpcdebug
/sbin/rpc.lockd
/sbin/rpc.statd
/usr/sbin/exportfs
/usr/sbin/nfsstat
/usr/sbin/nhfs*
/usr/sbin/rpc.mountd
/usr/sbin/rpc.nfsd
/usr/sbin/showmount
/usr/sbin/rpc.idmapd
/usr/sbin/rpc.gssd
/usr/sbin/rpc.svcgssd
%{_mandir}/*/*
%config /etc/rc.d/init.d/nfslock

%changelog
* Mon Mar 29 2005 Steve Dickson <SteveD@RedHat.com> 1.0.7-4
- Fixed a compile error on x86_64 machines in the gss code.
- Updated the statd-notify-hostname.patch to eliminate 
  a segmentation fault in rpc.statd when an network 
  interface was down. (bz 151828)

* Sat Mar 19 2005 Steve Dickson <SteveD@RedHat.com> 1.0.7-3
- Changed xlog to use LOG_INFO instead of LOG_DEBUG
  so debug messages will appear w/out any config
  changes to syslog.conf.
- Reworked how /etc/exports is setup (bz 151389)

* Wed Mar  2 2005 Steve Dickson <SteveD@RedHat.com> 1.0.7-2
- Tied the rpcsecgss debugging in with gssd and
  svcgssd debugging

* Mon Feb 14 2005 Steve Dickson <SteveD@RedHat.com>
- Added support to rpcgssd.init and rpcsvcgssd.init scripts
  to insmod security modules.
- Changed the nfs.init script to bring rpc.svcgssd up and down,
  since rpc.svcgssd is only needed with the NFS server is running.

* Tue Dec 14 2004 Steve Dickson <SteveD@RedHat.com>
- Fix problem in idmapd that was causing "xdr error 10008"
  errors (bz 142813)
- make sure the correct hostname is used in the SM_NOTIFY
  message that is sent from a rebooted server which has 
  multiple network interfaces. (bz 139101)

- Changed nfslock to send lockd a -KILL signal
  when coming down. (bz 125257)

* Thu Nov 11 2004 Steve Dickson <SteveD@RedHat.com>
- Replaced a memcopy with explicit assignments
  in getquotainfo() of rquotad to fix potential overflow
  that can occur on 64bit machines. (bz 138068)

* Mon Nov  8 2004 Steve Dickson <SteveD@RedHat.com>
- Updated to latest sourceforge code
- Updated to latest CITIT nfs4 patches

* Sun Oct 17 2004 Steve Dickson <SteveD@RedHat.com>
- Changed nfs.init to bring down rquotad correctly
  (bz# 136041)

* Thu Oct 14 2004 Steve Dickson <SteveD@RedHat.com>
- Added "$RQUOTAD_PORT" variable to nfs.init which
  allows the rpc.rquotad to use a predefined port
  (bz# 124676)

* Fri Oct  1 2004 <SteveD@RedHat.com
- Incorporate some clean up code from Ulrich Drepper (bz# 134025)
- Fixed the chkconfig number in the rpcgssd, rpcidmapd, and 
  rpcsvcgssd initscrpts (bz# 132284)

* Fri Sep 24 2004 <SteveD@RedHat.com>
- Make sure the uid/gid of nfsnobody is the
  correct value for all archs (bz# 123900)
- Fixed some security issues found by SGI (bz# 133556)

* Mon Aug 30 2004 Steve Dickson <SteveD@RedHat.com>
- Major clean up. 
- Removed all unused/old patches
- Rename and condensed a number of patches
- Updated to CITI's nfs-utils-1.0.6-13 patches

* Tue Aug 10 2004 Bill Nottingham <notting@redhat.com>
- move if..fi condrestart stanza to %%postun (#127914, #128601)

* Wed Jun 16 2004 <SteveD@RedHat.com>
- nfslock stop is now done on package removals
- Eliminate 3 syslog messages that are logged for
  successful events.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun 14 2004 <SteveD@RedHat.com>
- Fixed syntax error in nfs initscripts when
  NETWORKING is not defined
- Removed sync warning on readonly exports.
- Changed run levels in rpc initscripts.
- Replaced modinfo with lsmod when checking
  for loaded modules.

* Tue Jun  1 2004 <SteveD@RedHat.com>
- Changed the rpcgssd init script to ensure the 
  rpcsec_gss_krb5 module is loaded

* Tue May 18 2004 <SteveD@RedHat.com>
- Removed the auto option from MOUNTD_NFS_V2 and
  MOUNTD_NFS_V3 variables. Since v2 and v3 are on
  by default, there only needs to be away of 
  turning them off.

* Thu May 10 2004 <SteveD@RedHat.com>
- Rebuilt

* Thu Apr 15 2004 <SteveD@RedHat.com>
- Changed the permission on idmapd.conf to 644
- Added mydaemon code to svcgssd
- Updated the add_gssd.patch from upstream

* Wed Apr 14 2004 <SteveD@RedHat.com>
- Created a pipe between the parent and child so 
  the parent process can report the correct exit
  status to the init scripts
- Added SIGHUP processing to rpc.idmapd and the 
  rpcidmapd init script.

* Mon Mar 22 2004 <SteveD@RedHat.com>
- Make sure check_new_cache() is looking in the right place 

* Wed Mar 17 2004 <SteveD@RedHat.com>
- Changed the v4 initscripts to use $prog for the
  arugment to daemon

* Tue Mar 16 2004 <SteveD@RedHat.com>
- Made the nfs4 daemons initscripts work better when 
  sunrpc is not a module
- added more checks to see if modules are being used.

* Mon Mar 15 2004 <SteveD@RedHat.com>
- Add patch that sets up gssapi_mech.conf correctly

* Fri Mar 12 2004 <SteveD@RedHat.com>
- Added the shutting down of the rpc v4 daemons.
- Updated the Red Hat only patch with some init script changes.

* Thu Mar 11 2004 Bill Nottingham <notting@redhat.com>
- rpc_pipefs mounting and aliases are now in modutils; require that

* Thu Mar 11 2004 <SteveD@RedHat.com>
- Updated the gssd patch.

* Sun Mar  7 2004 <SteveD@RedHat.com>
- Added the addition and deletion of rpc_pipefs to /etc/fstab
- Added the addition and deletion of module aliases to /etc/modules.conf

* Mon Mar  1 2004 <SteveD@RedHat.com>
- Removed gssd tarball and old nfsv4 patch.
- Added new nfsv4 patches that include both the
   gssd and idmapd daemons
- Added redhat-only v4 patch that reduces the
   static librpc.a to only contain gss rpc related
   routines (I would rather have gssd use the glibc 
   rpc routines)
-Changed the gssd svcgssd init scripts to only
   start up if SECURE_NFS is set to 'yes' in
   /etc/sysconfig/nfs

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 12 2004 Thomas Woerner <twoerner@redhat.com>
- make rpc.lockd, rpc.statd, rpc.mountd and rpc.nfsd pie

* Wed Jan 28 2004 Steve Dickson <SteveD@RedHat.com>
- Added the NFSv4 bits

* Mon Dec 29 2003 Steve Dickson <SteveD@RedHat.com>
- Added the -z flag to nfsstat

* Wed Dec 24 2003  Steve Dickson <SteveD@RedHat.com>
- Fixed lockd port setting in nfs.int script

* Wed Oct 22 2003 Steve Dickson <SteveD@RedHat.com>
- Upgrated to 1.0.6
- Commented out the acl path for fedora

* Thu Aug  27 2003 Steve Dickson <SteveD@RedHat.com>
- Added the setting of lockd ports via sysclt interface
- Removed queue setting code since its no longer needed

* Thu Aug  7 2003 Steve Dickson <SteveD@RedHat.com>
- Added back the acl patch Taroon b2

* Wed Jul 23 2003 Steve Dickson <SteveD@RedHat.com>
- Commented out the acl patch (for now)

* Wed Jul 21 2003 Steve Dickson <SteveD@RedHat.com>
- Upgrated to 1.0.5

* Wed Jun 18 2003 Steve Dickson <SteveD@RedHat.com>
- Added security update
- Fixed the drop-privs.patch which means the chroot
patch could be removed.

* Mon Jun  9 2003 Steve Dickson <SteveD@RedHat.com>
- Defined the differ kinds of debugging avaliable for mountd in
the mountd man page. 

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun  3 2003 Steve Dickson <SteveD@RedHat.com>
- Upgraded to 1.0.3 
- Fixed numerous bugs in init scrips
- Added nfsstat overflow patch

* Thu Jan 23 2003 Tim Powers <timp@redhat.com> 1.0.1-2.9
- rebuild

* Fri Dec 13 2002 Daniel J Walsh <dwalsh@redhat.com>
- change init script to not start rpc.lock if already running

* Wed Dec 11 2002 Daniel J Walsh <dwalsh@redhat.com>
- Moved access code to be after dropping privs

* Mon Nov 18 2002 Stephen C. Tweedie <sct@redhat.com>
- Build with %configure
- Add nhfsgraph, nhfsnums and nhfsrun to the files list

* Mon Nov 11 2002 Stephen C. Tweedie <sct@redhat.com>
- Don't drop privs until we've bound the notification socket

* Thu Nov  7 2002 Stephen C. Tweedie <sct@redhat.com>
- Ignore SIGPIPE in rpc.mountd

* Thu Aug  1 2002 Bob Matthews <bmatthews@redhat.com>
- Add Sean O'Connell's <sean@ee.duke.edu> nfs control tweaks
- to nfs init script.

* Mon Jul 22 2002 Bob Matthews <bmatthews@redhat.com>
- Move to nfs-utils-1.0.1

* Mon Feb 18 2002 Bob Matthews <bmatthews@redhat.com>
- "service nfs restart" should start services even if currently 
-   not running (#59469)
- bump version to 0.3.3-4

* Wed Oct  3 2001 Bob Matthews <bmatthews@redhat.com>
- Move to nfs-utils-0.3.3
- Make nfsnobody a system account (#54221)

* Tue Aug 21 2001 Bob Matthews <bmatthews@redhat.com>
- if UID 65534 is unassigned, add user nfsnobody (#22685)

* Mon Aug 20 2001 Bob Matthews <bmatthews@redhat.com>
- fix typo in nfs init script which prevented MOUNTD_PORT from working (#52113)

* Tue Aug  7 2001 Bob Matthews <bmatthews@redhat.com>
- nfs init script shouldn't fail if /etc/exports doesn't exist (#46432)

* Fri Jul 13 2001 Bob Matthews <bmatthews@redhat.com>
- Make %pre useradd consistent with other Red Hat packages.

* Tue Jul 03 2001 Michael K. Johnson <johnsonm@redhat.com>
- Added sh-utils dependency for uname -r in nfs init script

* Tue Jun 12 2001 Bob Matthews <bmatthews@redhat.com>
- make non RH kernel release strings scan correctly in 
-   nfslock init script (#44186)

* Mon Jun 11 2001 Bob Matthews <bmatthews@redhat.com>
- don't install any rquota pages in _mandir: (#39707, #44119)
- don't try to manipulate rpc.rquotad in init scripts 
-   unless said program actually exists: (#43340)

* Tue Apr 10 2001 Preston Brown <pbrown@redhat.com>
- don't translate initscripts for 6.x

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
