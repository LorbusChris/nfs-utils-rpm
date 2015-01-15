#!/bin/sh

# extract configuration from /etc/sysconfig/nfs-utils and write
# environment to /run/sysconfig/nfs-utils to be used by systemd unit
# files.

nfs_config=/etc/sysconfig/nfs
if test -r $nfs_config; then
    . $nfs_config
fi

[ -n "$LOCKDARG" ] && /sbin/modprobe lockd $LOCKDARG
if [ -n "$LOCKD_TCPPORT" -o -n "$LOCKD_UDPPORT" ]; then
    [ -z "$LOCKDARG" ] && /sbin/modprobe lockd $LOCKDARG
    [ -n "$LOCKD_TCPPORT" ] && \
        /sbin/sysctl -w fs.nfs.nlm_tcpport=$LOCKD_TCPPORT >/dev/null 2>&1
    [ -n "$LOCKD_UDPPORT" ] && \
        /sbin/sysctl -w fs.nfs.nlm_udpport=$LOCKD_UDPPORT >/dev/null 2>&1
fi

if [ -n "$NFSD_V4_GRACE" ]; then
    grace="-G $NFSD_V4_GRACE"
fi

if [ -n "$NFSD_V4_LEASE" ]; then
    lease="-L $NFSD_V4_LEASE"
fi

if [ -n "$RPCNFSDCOUNT" ]; then
    nfsds=$RPCNFSDCOUNT
else
    nfsds=8
fi

if [ -n "$RPCNFSDARGS" ]; then
    nfsdargs="$RPCNFSDARGS $grace $lease $nfsds "
else
    nfsdargs="$grace $lease $nfsds "
fi

mkdir -p /run/sysconfig
{
echo RPCNFSDARGS="$nfsdargs"
echo RPCMOUNTDARGS="$RPCMOUNTDOPTS"
echo STATDARGS="$STATDARG"
echo SMNOTIFYARGS="$SMNOTIFYARGS"
echo RPCIDMAPDARGS="$RPCIDMAPDARGS"
echo RPCGSSDARGS="$RPCGSSDARGS"
echo RPCSVCGSSDARGS="$RPCSVCGSSDARGS"
echo BLKMAPDARGS="$BLKMAPDARGS"
} > /run/sysconfig/nfs-utils
