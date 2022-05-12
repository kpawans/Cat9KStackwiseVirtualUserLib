'''
svl_job.py

This job is to launch the script: scripts/stackwise_virtual.py.

This should be run in your python environment with pyats installed. 

Run this job from parent directory:
    pyats run job job/svl_job.py --testbed ./testbed/9500_sv_tb.yaml

Support Platform: Linux/MAC/Ubuntu

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html
# for how job files work

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pawansi@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import os
from pyats.easypy import run

# compute the script path from this location
SCRIPT_PATH = os.path.dirname("./")

def main(runtime):
    '''job file entrypoint'''
    
    # run script
    run(testscript= os.path.join(SCRIPT_PATH, 
                                 'scripts/stackwise_virtual.py'),
        runtime = runtime)
