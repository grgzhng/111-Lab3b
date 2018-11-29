# NAME: Clayton Chu, George Zhang
# EMAIL: claytonchu99@gmail.com, georgezhang@ucla.edu
# ID: 104906833, 504993197

#!/usr/bin/python3

import sys
import csv
import os

sb = None
freeBlocks = []
freeInodes = []
inodes = []
indirects = []
dirents = []
unallocInodeNums = []
allocInodes = []
err = 0


class SuperBlock:
    def __init__(self, line):
        self.block_count = int(line[1])
        self.inode_count = int(line[2])
        self.block_size = int(line[3])
        self.inode_size = int(line[4])
        self.blocks_per_group = int(line[5])
        self.inodes_per_group = int(line[6])
        self.first_inode = int(line[7])


class Dirent:
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
        self.addresses = list(map(int, line[12:24]))
        self.single_ind = int(line[24])
        self.double_ind = int(line[25])
        self.triple_ind = int(line[26])

    def __str__(self):
        return str(self.type)


class Indirect:
    def __init__(self, line):
        self.inode_num = int(line[1])
        self.level = int(line[2])
        self.offset = int(line[3])
        self.block_num = int(line[4])
        self.reference_num = int(line[5])


def exitWithError(msg):
    sys.stderr.write(msg)
    exit(1)


def examineInodes():
    global inodes, freeInodes, err, unallocInodeNums, allocInodes

    unallocInodeNums = freeInodes
    for inode in inodes:
        if inode.type == '0':
            if inode.inode_num not in freeInodes:
                print("UNALLOCATED INODE %s NOT ON FREELIST" % inode.inode_num)
                unallocInodeNums.append(inode.inode_num)
                err += 1
        else:
            if inode.inode_num in freeInodes:
                print("ALLOCATED INODE %s ON FREELIST" % inode.inode_num)
                unallocInodeNums.remove(inode.inode_num)
                err += 1
            allocInodes.append(inode)

    # check bitmap
    for inode in range(sb.first_inode, sb.inode_count):
        isUsed = False if len(
            list(filter(lambda x: x.inode_num == inode, inodes))) <= 0 else True
        if not isUsed and inode not in freeInodes:
            print("UNALLOCATED INODE %s NOT ON FREELIST" % inode)
            unallocInodeNums.append(inode)
            err += 1


def examineBlocks():
    global err
    legalBlocks = {}
    types = ["", "INDIRECT ", "DOUBLE INDIRECT ", "TRIPLE INDIRECT "]

    def check(block, inodeNum, offset, typeBlock):
        global err
        maxBlock = sb.block_count - 1

        if block != 0:
            if block > maxBlock:
                print("INVALID {}BLOCK {} IN INODE {} AT OFFSET {}".format(
                    types[typeBlock], block, inodeNum, offset))
                err += 1
            elif block < 8:
                print("RESERVED {}BLOCK {} IN INODE {} AT OFFSET {}".format(
                    types[typeBlock], block, inodeNum, offset))
                err += 1
            elif block in legalBlocks:
                legalBlocks[block].append((inodeNum, offset, typeBlock))
            else:
                legalBlocks[block] = [(inodeNum, offset, typeBlock)]

    for inode in inodes:
        for offset, block in enumerate(inode.addresses):
            check(block, inode.inode_num, offset, 0)
        check(inode.single_ind, inode.inode_num, 12, 1)
        check(inode.double_ind, inode.inode_num, 268, 2)
        check(inode.triple_ind, inode.inode_num, 65804, 3)

    for indirectBlock in indirects:
        check(indirectBlock.reference_num, indirectBlock.inode_num,
              indirectBlock.offset, indirectBlock.level)

    for block in range(8, sb.block_count):
        if block not in freeBlocks and block not in legalBlocks:
            print("UNREFERENCED BLOCK {}".format(block))
            err += 1
        elif block in freeBlocks and block in legalBlocks:
            print("ALLOCATED BLOCK {} ON FREELIST".format(block))
            err += 1
        elif block in legalBlocks and len(legalBlocks[block]) > 1:
            inodeList = legalBlocks[block]
            for inodeNum, offset, typeBlock in inodeList:
                print("DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(
                    types[typeBlock], block, inodeNum, offset))
                err += 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exitWithError("Usage: ./lab3b filename\n")

    fname = sys.argv[1]
    if not os.path.isfile(fname):
        exitWithError("File doesn't exist\n")

    # handle parsing of csv & moving into data structures
    f = open(fname, 'r')
    if not f:
        exitWithError("Failed to open file\n")
    if os.path.getsize(fname) <= 0:
        exitWithError("File is empty\n")

    # use csv to read lines of file and add them to d.s.
    reader = csv.reader(f, delimiter=',')
    for line in reader:
        if len(line) <= 0:
            exitWithError("File has a blank line\n")
        if line[0] == 'SUPERBLOCK':
            sb = SuperBlock(line)
        elif line[0] == 'GROUP':
            pass
        elif line[0] == 'BFREE':
            freeBlocks.append(int(line[1]))
        elif line[0] == 'IFREE':
            freeInodes.append(int(line[1]))
        elif line[0] == 'DIRENT':
            dirents.append(Dirent(line))
        elif line[0] == 'INODE':
            inodes.append(Inode(line))
        elif line[0] == 'INDIRECT':
            indirects.append(Indirect(line))
        else:
            exitWithError("Unrecognized line in csv - unable to be parsed\n")

    examineInodes()
