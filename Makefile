# Makefile for source rpm: nfs-utils
# $Id$
NAME := nfs-utils
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
