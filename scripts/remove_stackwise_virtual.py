'''
remove_stackwise_virtual.py

This script is ro remove the stackwise virtual configs from a Stackwise Virtual HA Switch.
The Switches access and connection details need to be provided in the testbed file. The sample testbed file is present in 
testbed directory for 9500/9600 switches types.

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pawansi@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging

from pyats import aetest
# create a logger for this module
Logger = logging.getLogger(__name__)
from svlservices.svlservice import StackWiseVirtual
from pyats.aetest.steps import Steps

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        '''
        establishes connection to all your testbed devices.
        '''
        # make sure testbed is provided
        assert testbed, 'Testbed is not provided!'

        #initilize StackWiseVirtual Class
        svl_handle = StackWiseVirtual(testbed)
        Logger.info(svl_handle)
        self.parent.parameters['svl_handle'] = svl_handle

class svl_config_removal(aetest.Testcase):
    '''svl_config_removal
        1. This testcase remove preconfigured svl configs of stackwose virtual switch.
        2. Validate that the configs are removed from both the switches.
    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self,svl_handle):
        svl_handle.get_device_pairs()

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test_validate_links_for_stackwise_virtual_pair(self,svl_handle):
        '''
            This is a precheck test to check if the links provided in the testbed yaml file are correct.
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of Stackwise Virtual status before removing config",continue_= True) as step:
                if not svl_handle.check_links(stackpair):
                    Logger.error("The devices provided to be paired into SVL does not have any links connected to eachothers")
                    result=False
                    step.failed("The Stackwise Cirtual Links Prechecks failed for VirtualPair: {}".format(stackpair))
        if not result:
            self.failed("Validation of Stackwise virtual config links failed")

    @aetest.test
    def test_validate_console_connectivity_to_switches(self,svl_handle):
        '''
            This is a precheck test to check if connesol connectivity is established with teh devoces
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of console connectivity on Stackwise Virtual device pairs",continue_= True) as step:
                if not svl_handle.connect_to_stackpair(stackpair):
                    result=False
                    step.failed("Could not connect to devices, Can not proceed. for stackwise virtual pair :{}".format(stackpair))
        if not result:
            self.failed("Console connectivity to some or all of the devices could not  be established", goto = ['common_cleanup'])

    @aetest.test
    def test_validate_configs_for_stackwise_virtual_pair(self,svl_handle):
        '''
            This is a precheck test to verify if the stackwise virtual configs are presnt on the switches
        '''
        result=True
        steps = Steps()
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of Stackwise Virtual status before removing config",continue_= True) as step:
                if not svl_handle.check_stackwise_virtual_confgured(stackpair):
                    result=False
                    step.failed("Stackwise Virtual configs are not present on one or both of the switches of stackpair: {}".format(stackpair))
        if not result:
            self.failed("Validation of Stackwise Virtual config failed ", goto = ['common_cleanup'])

    @aetest.test
    def test_remove_stackwiseVirtual_configs_and_make_them_independent(self,svl_handle):
        '''
            This test removes the stack-wise virtual configs from the switches and save and reload the switchs to apply the configs.
            After the test the switch will be independent. 
            The test depend on the links config provided in the yaml file. 
            Please ensure correct links are provided in the yamls file
        '''
        result=True
        steps = Steps()
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Stackwise Virtual Config remoaval",continue_= True) as step:
                #Remove Stackwise Virtual Config!!
                if not svl_handle.disable_svl_config(stackpair):
                    result=False
                    step.failed("StackwiseVirtual Configs  removal failed from the one of both switches.")

                if not svl_handle.save_config_and_reload(stackpair,reloadAsync=True):
                    result=False
                    step.failed("StackwiseVirtual save config and reload, for stackwise virtual config is failed on one or both switches.")
                else:
                    Logger.info("StackwiseVirtual configs are successfully removed from the switches.")

        if not result:
            self.failed("Stackwise Virtual config removal failed ", goto = ['common_cleanup'])
        else:
            self.passed("successfully removed stackwise virtual configs from all the stack pairs.")

    @aetest.test
    def test_reconnect_to_switches_after_removing_configs(self,svl_handle):
        '''
            This is a precheck test to check if connesol connectivity is established with teh devoces
        '''
        steps = Steps()
        result=True
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of console connectivity on Stackwise Virtual device pairs",continue_= True) as step:
                if not svl_handle.connect_to_stackpair(stackpair):
                    result=False
                    step.failed("Could not connect to devices, Can not proceed. for stackwise virtual pair :{}".format(stackpair))
        if not result:
            self.failed("Console connectivity to some or all of the devices could not  be established", goto = ['common_cleanup'])

    @aetest.test
    def test_validate_configs_removed_for_stackwise_virtual_pair(self,svl_handle):
        '''
            This is a precheck test to verify if the stackwise virtual configs are presnt on the switches
        '''
        result=True
        steps = Steps()
        for stackpair in svl_handle.device_pair_list:
            with steps.start("Validation of Stackwise Virtual status before removing config",continue_= True) as step:
                if svl_handle.check_stackwise_virtual_confgured(stackpair):
                    result=False
                    step.failed("Stackwise Virtual configs are still present on one or both of the switches of stackpair: {}".format(stackpair))
        if not result:
            self.failed("Validation of Stackwise Virtual config are not removed ")

    @aetest.cleanup
    def cleanup(self):
        pass
    
class common_cleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, svl_handle):
        logging.info("Disconnected from the device...Into common cleanup section")


if __name__ == '__main__':
    # for stand-alone execution
    import argparse
    from pyats import topology

    parser = argparse.ArgumentParser(description = "standalone parser")
    parser.add_argument('--testbed', dest = 'testbed',
                        help = 'testbed YAML file',
                        type = topology.loader.load,
                        default = None)

    # do the parsing
    args = parser.parse_known_args()[0]

    aetest.main(testbed = args.testbed)

