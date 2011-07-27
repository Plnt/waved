#!/usr/bin/env python

import operator
import sys
import os
import urllib
import md5
import optparse

#import pprint

fhashes = {}


def load_hashes(file_in, file_version):

	global fhashes

	f = open("def/" + file_in + "/" + file_in + "-" + file_version)
	while 1:
		line = f.readline().strip()
		if not line:
			break
		lines = line.split(";")
		#print lines
		if (lines[0] == "1"):
			if (lines[1] in fhashes):
				#print lines[0] + " " + file_version + " " + lines[1]
				fhashes[lines[1]][file_version] = lines[2]
			else:
				fhashes[lines[1]] = {file_version: lines[2]}

	f.close()


def count_hashes():

	global fhashes_diff
	fhashes_local_diff = {}

	for file_act in fhashes:
		fhashes_local = {}
		for ver_act in fhashes[file_act]:
			fhashes_local[fhashes[file_act][ver_act]] = 1
		#fhashes[file_act]['total'] = len(fhashes_local)
		fhashes_local_diff[file_act] = len(fhashes_local)

	fhashes_diff = sorted(fhashes_local_diff.iteritems(), key=operator.itemgetter(1), reverse = True)


# ---

# Parse command line arguments
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-v", "--verbose",
	action="store_true", dest="verbose", default=False,
	help="print more verbose messages")
parser.add_option("-a", "--application",
        dest="application", action="store",
        help="web application (i.e. roundcube, phpbb2, phpbb3, ..)")

(options, args) = parser.parse_args()

#print options
#print args

if len(args) != 1:
	parser.error("incorrect number of arguments")

if options.application == None:
	parser.error("missing web application name")

app_name = options.application
url_finger = args[0]

url_count = 10

# Load hashes for all versions of selected web application
dirlist = os.listdir("def/" + app_name)
for file_act in dirlist:
	app_version = file_act.split("-", 1)[1]
	load_hashes(app_name, app_version)

# Count which files have the biggest differences in their hashes
count_hashes()

#pprint.pprint(fhashes)
#pprint.pprint(fhashes_diff)

ver_breakdown = {}

url_count_tmp = url_count

i = 0
while (url_count_tmp > 0):
	#print fhashes_diff[i]
	f = urllib.urlopen(url_finger + fhashes_diff[i][0])
	if options.verbose:
		print("%i %s" % (f.getcode(), fhashes_diff[i]))
	if f.getcode() == 200:
		s = f.read()
		s_md5 = md5.new(s).hexdigest()
		for ver_act in fhashes[fhashes_diff[i][0]]:
			if (s_md5 == fhashes[fhashes_diff[i][0]][ver_act]):
				if options.verbose:
					print ver_act
				if ver_act in ver_breakdown:
					ver_breakdown[ver_act] += 1
				else:
					ver_breakdown[ver_act] = 1
		url_count_tmp = url_count_tmp - 1

	i = i + 1

# Sort versions breakdown
ver_breakdown_sorted = sorted(ver_breakdown.iteritems(), key=operator.itemgetter(1), reverse = True)
#pprint.pprint(ver_breakdown_sorted)

if options.verbose:
	print

for i in ver_breakdown_sorted:
	print("%s %i%%" % (i[0], 100 / url_count * i[1]))
