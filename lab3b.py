# NAME: Clayton Chu, George Zhang
# EMAIL: claytonchu99@gmail.com, georgezhang@ucla.edu
# ID: 104906833, 504993197

#!/usr/bin/python

import sys
import csv
import os

sb = None
freeBlocks = []
freeInodes = []
inodes = []
indirects = []
directories = []


class SuperBlock:
    def __init__(self, line):
        self.block_count = int(line[1])
        self.inode_count = int(line[2])
        self.block_size = int(line[3])
        self.inode_size = int(line[4])
        self.blocks_per_group = int(line[5])
        self.inodes_per_group = int(line[6])
        self.first_inode = int(line[7])


class Direct:
	def __init__(self, line):
		self.parent_inode = int(line[1])
		self.logical_offset = int(line[2])
		self.file_num = int(line[3])
		self.rec_len = int(line[4])
		self.name_len = int(line[5])
		self.name = line[6].rstrip()


class Inode:
	def __init__(self, line):
		self.inode_num = int(line[1])
		self.type = line[2]
		self.mode = line[3]
		self.owner = int(line[4])
		self.group = int(line[5])
		self.link_count = int(line[6])
		self.ctime = line[7]
		self.mtime = line[8]
		self.atime = line[9]
		self.size = int(line[10])
		self.blocks_num = int(line[11])
		self.addresses = []
        for address in line[12:24]:
			self.addresses.append(int(address))
		self.single_ind=int(line[24])
		self.double_ind=int(line[25])
		self.triple_ind=int(line[26])


def exitWithError(msg):
    sys.stderr.write(msg)
    exit(1)


if __name__ == '__main__':
    if(len(sys.argv)) != 2:
        exitWithError("Usage: ./lab3b filename\n")

    fname=sys.argv[1]
    if not os.path.isfile(fname):
        exitWithError("File doesn't exist\n")

    global sb, freeBlocks, freeInodes, inodes, indirects

    # handle parsing of csv & moving into data structures
    f=open(fname, 'r')
    if not f:
        exitWithError("Failed to open file\n")
    if os.path.getsize(fname) <= 0:
        exitWithError("File is empty\n")

	# use csv to read lines of file and add them to d.s.
    reader=csv.reader(f, delimiter=',')
    for line in reader:
        if len(row) <= 0:
            exitWithError("File has a blank line\n")
        if line[0] == 'SUPERBLOCK':
            sb=SuperBlock(line)
		elif line[0] == 'GROUP':
			pass
		elif line[0] == 'BFREE':
			freeBlocks.append(int(line[1]))
		elif line[0] == 'IFREE':
			freeInodes.append(int(line[1]))
		elif line[0] == 'DIRECT':
			directories.append(Direct(line))
		elif line[0] == 'INODE':
			inodes.append(Inode(line))
		elif line[0] == 'INDIRECT':
			indirects.append(Indirect(line))
		else:
			exitWithError("Unrecognized line in csv - unable to be parsed\n")
