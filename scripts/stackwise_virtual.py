'''
ls.py

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/aetest/index.html
# for documentation on pyATS test scripts

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2019, Cisco Systems Inc.'
__contact__ = ['pyats-support-ext@cisco.com']
__credits__ = ['list', 'of', 'credit']
__version__ = 1.0

import logging

from pyats import aetest
# create a logger for this module
logger = logging.getLogger(__name__)
from svlservices.svlservice import StackWiseVirtual


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
        print(svl_handle)
        self.parent.parameters['svl_handle'] = svl_handle

class svlformation(aetest.Testcase):
    '''svlformation

    < docstring description of this testcase >

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
    def test(self,svl_handle):
        stackpair = svl_handle.device_pair_list[0]
        if not svl_handle.check_links(stackpair):
            Logger.error("The devices provided to be paired into SVL does not have any links connected to eachothers")
            self.failed("The Prechecks failed.", goto = ['CommonCleanup'])

    @aetest.test
    def test(self,svl_handle):
        stackpair = svl_handle.device_pair_list[0]
        if not svl_handle.check_min_version_req(stackpair):
            self.failed("Minimum Version check failed ", goto = ['CommonCleanup'])

    @aetest.test
    def test(self,svl_handle):
        stackpair = svl_handle.device_pair_list[0]
        if not svl_handle.configure_svl_step1(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])
        if not svl_handle.save_config_and_reload(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])

        if not svl_handle.configure_svl_step2_svllinkconfig(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])
        if not svl_handle.save_config_and_reload(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])

        if not svl_handle.configure_svl_step3_dad_linkconfig(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])

        if not svl_handle.save_config_and_reload(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.", goto = ['CommonCleanup'])

        if not svl_handle.configure_svl_step4_validate_svl(stackpair):
            self.failed("Step1 Config failed, Revover Mannuly.")

    @aetest.cleanup
    def cleanup(self):
        pass
    

class svltest(aetest.Testcase):
    '''svltest

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    

class svlremove(aetest.Testcase):
    '''svlremove

    < docstring description of this testcase >

    '''

    # testcase groups (uncomment to use)
    # groups = []

    @aetest.setup
    def setup(self):
        pass

    # you may have N tests within each testcase
    # as long as each bears a unique method name
    # this is just an example
    @aetest.test
    def test(self):
        pass

    @aetest.cleanup
    def cleanup(self):
        pass
    


class CommonCleanup(aetest.CommonCleanup):
    '''CommonCleanup Section

    < common cleanup docstring >

    '''

    # uncomment to add new subsections
    # @aetest.subsection
    # def subsection_cleanup_one(self):
    #     pass

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

