#!/usr/bin/env python

import os
import sys
from glob import glob
from pprint import pprint

mlist = []
ilist = glob('inputfiles/inp.*')
for inpf in ilist:
    with open(inpf, 'r') as f:
        for line in f:
            sline = line.split()
            if sline[0] == 'input_fitsimage' and sline[1].endswith('.tar.gz'):
                mlist.append(sline[1])
            else:
                pass
print('Models to be deleted:')
if len(mlist) == 0:
    sys.exit('None.')
pprint(mlist)
raw_input("Press Enter to continue...")
symba_exec = 'singularity exec /cvmfs/singularity.opensciencegrid.org/mjanssen2308/symba:latest '
for mod in mlist:
    os.system('{0} irm {1} 2>/dev/null'.format(symba_exec, mod))
print('')
