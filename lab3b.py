# NAME: Clayton Chu, George Zhang
# EMAIL: claytonchu99@gmail.com, georgezhang@ucla.edu
# ID: 104906833, 504993197

#!/usr/bin/python

import sys
import csv
import os

def exitWithError(msg):
  sys.stderr.write(msg)
  exit(1)

if __name__ == '__main__':
  if(len(sys.argv)) != 2:
    exitWithError("Usage: ./lab3b FILENAME\n")