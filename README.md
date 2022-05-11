#==========================Ready for use============================================================
# for help Reachout to pawansi@cisco.com
#===================================================================================================
https://www.cisco.com/c/dam/en/us/td/i/300001-400000/350001-360000/354001-355000/354879.eps/_jcr_content/renditions/354879.jpg
#  
#   |-------|--------Dual Active Detection Link (DAD-LINK)------------------|-------|
#   |Switch1|----------Stackwise-Virtual link (STACKWISEVIRTUAL-LINK)-------|Switch2|
#   |-------|----------Stackwise-Virtual link (STACKWISEVIRTUAL-LINK)-------|-------|
#
#    Each Dual Active Detection must have "DAD-LINK" keyword in link description text
#    Each Dual Stackwise-virtual  must have "STACKWISEVIRTUAL-LINK" keyword in link description text
#    Link number should switch index appended for each link: 1/0/48  --> for switch1 1/1/0/48
#                                                                    --> for switch2 2/1/0/48
#===================================================================================================
https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9500/software/release/16-11/configuration_guide/ha/b_1611_ha_9500_cg/configuring_cisco_stackwise_virtual.html

1. Creating a Stackwise Virtual from two 9K switches. Details provided in testbed yaml.
2. The project used Cisco pyats environment, or use it as a container on any linux machine.
3. To install the execution environment, first install the Python3.7 or above on the execution server and then run the setup.sh tool to install the pyats environment. 

#Code Checkout:
Checkout the code with git or download from github directly.

git clone git@github.com:kpawans/stackwiseVirtualFormation.git

cd stackwiseVirtualFormation

#to run the setup installer:
./setup.sh

#source your python/pyats env
source pythonenv/bin/activate

#Create or Setup your testbed yaml file for the switch pair. Refer sample file: testbed/9600_sv_tb.yaml

#Running scripts
pyats run job <joblocation> --testbed <testbedlocation>

#Launch your svlbuilder script.

pyats run job job/svl_job.py --testbed ./testbed/9600_sv_tb.yaml

#to Cleanup svlconfig from svl pair

pyats run job job/svl_remove_job.py --testbed ./testbed/9600_sv_tb.yaml

#To use this as a library:
from svlservices.svlservice import StackWiseVirtual


#==============================================================================================================================================
#=============================== A Successfull Sample report will be generated as below========================================================
#==============================================================================================================================================
2022-05-11 13:07:25,285: %UNICON-INFO: +++ SWITCH-1svl with via 'a' and alias 'a': executing command 'show stackwise-virtual' +++
show stackwise-virtual
Stackwise Virtual Configuration:
--------------------------------
Stackwise Virtual : Enabled
Domain Number :	2  

Switch	Stackwise Virtual Link	Ports
------	----------------------	------
1    	1                   	TenGigabitEthernet1/0/33    
      	                      	TenGigabitEthernet1/0/40    
2    	1                   	TenGigabitEthernet2/0/33    
      	                      	TenGigabitEthernet2/0/40    

Switch#

2022-05-11 13:07:25,639: %UNICON-INFO: +++ SWITCH-1svl with via 'a' and alias 'a': executing command 'show stackwise-virtual neighbors' +++
show stackwise-virtual neighbors
Stackwise Virtual Link(SVL) Neighbors Information:
--------------------------------------------------
Switch	SVL	Local Port                         Remote Port
------	---	----------                         -----------
1    	1	TenGigabitEthernet1/0/33           TenGigabitEthernet2/0/33         
      	   	TenGigabitEthernet1/0/40           TenGigabitEthernet2/0/40         
2    	1	TenGigabitEthernet2/0/33           TenGigabitEthernet1/0/33         
      	   	TenGigabitEthernet2/0/40           TenGigabitEthernet1/0/40         

Switch#

2022-05-11 13:07:25,985: %UNICON-INFO: +++ SWITCH-1svl with via 'a' and alias 'a': executing command 'show stackwise-virtual dual-active-detection' +++
show stackwise-virtual dual-active-detection
In dual-active recovery mode: No
Recovery Reload: Enabled

Dual-Active-Detection Configuration:
-------------------------------------
Switch	Dad port			Status
------	------------			---------
1 	TenGigabitEthernet1/0/24  	up     
2 	TenGigabitEthernet2/0/24  	up     

Switch#
2022-05-11T13:07:26: %EASYPY-INFO: Job finished. Wrapping up...
2022-05-11T13:07:27: %EASYPY-INFO: Creating archive file: /Users/pawansingh/.pyats/archive/22-May/svl_job.2022May11_12:45:36.973477.zip
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: |                                Easypy Report                                 |
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: pyATS Instance   : /Library/Frameworks/Python.framework/Versions/3.7
2022-05-11T13:07:27: %EASYPY-INFO: Python Version   : cpython-3.7.9 (64bit)
2022-05-11T13:07:27: %EASYPY-INFO: CLI Arguments    : /Library/Frameworks/Python.framework/Versions/3.7/bin/pyats run job job/svl_job.py --testbed ./testbed/9500_sv_tb.yaml
2022-05-11T13:07:27: %EASYPY-INFO: User             : pawansingh
2022-05-11T13:07:27: %EASYPY-INFO: Host Server      : PAWANSI-M-5DCS
2022-05-11T13:07:27: %EASYPY-INFO: Host OS Version  : Mac OSX 10.16 (x86_64)
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: Job Information
2022-05-11T13:07:27: %EASYPY-INFO:     Name         : svl_job
2022-05-11T13:07:27: %EASYPY-INFO:     Start time   : 2022-05-11 12:45:40.701014
2022-05-11T13:07:27: %EASYPY-INFO:     Stop time    : 2022-05-11 13:07:26.405121
2022-05-11T13:07:27: %EASYPY-INFO:     Elapsed time : 1305.704107
2022-05-11T13:07:27: %EASYPY-INFO:     Archive      : /Users/pawansingh/.pyats/archive/22-May/svl_job.2022May11_12:45:36.973477.zip
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: Total Tasks    : 1 
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: Overall Stats
2022-05-11T13:07:27: %EASYPY-INFO:     Passed     : 3
2022-05-11T13:07:27: %EASYPY-INFO:     Passx      : 0
2022-05-11T13:07:27: %EASYPY-INFO:     Failed     : 0
2022-05-11T13:07:27: %EASYPY-INFO:     Aborted    : 0
2022-05-11T13:07:27: %EASYPY-INFO:     Blocked    : 0
2022-05-11T13:07:27: %EASYPY-INFO:     Skipped    : 0
2022-05-11T13:07:27: %EASYPY-INFO:     Errored    : 0
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO:     TOTAL      : 3
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: Success Rate   : 100.00 %
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: |                             Task Result Summary                              |
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: Task-1: stackwise_virtual.common_setup                                    PASSED
2022-05-11T13:07:27: %EASYPY-INFO: Task-1: stackwise_virtual.svlformation_and_validation                     PASSED
2022-05-11T13:07:27: %EASYPY-INFO: Task-1: stackwise_virtual.common_cleanup                                  PASSED
2022-05-11T13:07:27: %EASYPY-INFO: 
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: |                             Task Result Details                              |
2022-05-11T13:07:27: %EASYPY-INFO: +------------------------------------------------------------------------------+
2022-05-11T13:07:27: %EASYPY-INFO: Task-1: stackwise_virtual
2022-05-11T13:07:27: %EASYPY-INFO: |-- common_setup                                                          PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   `-- commonsetup_initialize_testbed                                    PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |-- svlformation_and_validation                                           PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- setup_make_svl_pairs_from_testbed_input                           PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- test_pre_check_stackwise_virtual_links                            PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- test_validate_console_connectivity_to_switches                    PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- test_preches_validate_platform_and_version_match_and_minimu...    PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- test_configure_stackwise_virtual_configs_bringup_stackwiseV...    PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   |-- test_validate_configs_for_stackwise_virtual_pair                  PASSED
2022-05-11T13:07:27: %EASYPY-INFO: |   `-- test_configure_stackwise_virtual_configs_and_validate             PASSED
2022-05-11T13:07:27: %EASYPY-INFO: `-- common_cleanup                                                        PASSED
2022-05-11T13:07:27: %EASYPY-INFO:     `-- disconnect_from_devices                                           PASSED
2022-05-11T13:07:27: %EASYPY-INFO: Sending report email...
2022-05-11T13:07:27: %EASYPY-INFO: Missing SMTP server configuration, or failed to reach/authenticate/send mail. Result notification email failed to send.
2022-05-11T13:07:27: %EASYPY-INFO: Done!
#================================================
