#Stackwise vitual Class. Models two switches as one HA device.
from threading import Thread
from pyats.topology import loader
import logging
import re
import time
from unicon.eal.dialogs import Statement, Dialog

SVLVERSION_9500="16.8.1"
SVLVERSION_9400="16.9.1"
SVLVERSION_9600="16.12.1"

PLATFORMVERSIONREFERENCE=[
	{	"platform": ["C9500-40X","C9300-24P"],
		"ref_version": SVLVERSION_9500
	},
	{	"platform": ["C9407R"],
		"ref_version": SVLVERSION_9400
	},
	{	"platform": ["C9606R"],
		"ref_version": SVLVERSION_9600
	}
]

DIALOG_CONFIRM = Dialog([
        Statement(pattern=r'^.*continue\?\[y/n\]\?\s*\[yes\]\:.*$',
                  action="sendline(yes)",
                  loop_continue=True,
                  continue_timer=False)])

DIALOG_CONFIRM1 =  Dialog([
        Statement(pattern=r"^.*continue\?\[y/n\]\?.*$",
                  action="sendline(y)",
                  loop_continue=True,
                  continue_timer=False),
        Statement(pattern=r"^.*\[confirm\(\(y/n\)?\].*$",
                  action="sendline(y)",
                  loop_continue=True,
                  continue_timer=False)])

Logger = logging.getLogger(__name__)
class MultiUserThreadWithReturn(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._Thread__target = target
        self._Thread__args = args
        self._Thread__kwargs = kwargs
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return

#Class for SVL
class StackWiseVirtual(object):
	def __init__(self, testbed):
		self.testbed=testbed
		self.device_pair_list=[]

	def get_device_pairs(self):
		for pair in self.testbed.custom['switchstackinggroups']:
			if pair["numberofswitches"] != len(pair["switchs"]): 
				Logger.error(
					"Testbed File Validation Error: The number of devices {}, an count devices provided {} does not match".format(
								pair["numberofswitches"],pair["switchs"]))
				raise
			dev_stack={}
			count=1
			for switch in pair["switchs"]:
				dev_stack["switch{}".format(count)] = switch
				count=count+1
			self.device_pair_list.append(dev_stack)

	def get_device_version(self, dev):

		output=self.testbed.devices[dev].execute("show version")
		version = re.findall("Cisco IOS XE Software, Version\s+(\S+)",str(output))[0]
		model_number = re.findall("Model Number\s+:\s+(\S+)",str(output))[0]
		return dict(version=version,model=model_number)

	def check_links(self, stackpair):
		links_count=0
		for links in self.testbed.devices[stackpair["switch1"]]:
			if self.testbed.devices[stackpair["switch2"]] in links.remote_devices:
				links_count = links_count + 1
		Logger.info("Number of links found between the switches:{}".format(links_count))
		if links_count:
			return True
		else:
			Logger.info("No Links present between the devices, not good for forming the SVL")
			return False	

	def check_min_version_req(self, stackpair):
		#Check for switch 1.
		if not self.connect_to_stackpair(stackpair):
			Logger.error("Could not connect to devices, Can not proceed.")
			return False
		switches=[stackpair["switch1"], stackpair["switch2"]]
		dev_details=[]
		for dev in switches:
			device_details = self.get_device_version(dev)
			dev_details.append(device_details)
			found=False
			for item in PLATFORMVERSIONREFERENCE:
				if device_details['model'] in item["platform"]:
					found = True
					if device_details['version'] < item["ref_version"]:
						Logger.error("The Device Version is below minimum supported version for Stackwise Virtual,"+
									 " First upgrade the device to minimum supported version:{}".forma(item["ref_version"]))
						return False
					else:
						Logger.info("Device Version:{} is higher then minimum required version:{}".format(
								device_details['version'] ,item["ref_version"]))
			if not found:
				Logger.warning("The Platform not found in reference list, this may not support Stackwise Virtual")
				return False

		#check for platform and version is same for bothe switches
		dd=dev_details[0]
		for devdetail in dev_details:
			if dd != devdetail:
				Logger.error("The device version or Platform does not match for the two stack members")
				Logger.error("\t Switch1 Details: {}\n Switch2 Details: {}".format(dd,devdetail))
				return False
		return True

	def check_valid_link_types(self, stackpair):
		pass

	def check_valid_link_types(self, stackpair):
		pass

	def connect_to_stackpair(self,stackpair):
		if not self.testbed.devices[stackpair["switch1"]].connected:
			dev_detail = self.testbed.devices[stackpair["switch1"]].connect()
		if not self.testbed.devices[stackpair["switch2"]].connected:
			dev_detail = self.testbed.devices[stackpair["switch2"]].connect()
		return True

	def disconnect_from_stackpair(self,stackpair):
		self.testbed.devices[stackpair["switch1"]].disconnect()
		self.testbed.devices[stackpair["switch2"]].disconnect()
		return True

	def save_config_and_reload(self, stackpair):
		self.testbed.devices[stackpair["switch1"]].execute("write memory")
		self.testbed.devices[stackpair["switch2"]].execute("write memory")
		
		#Reload bothe switches
		try:
			self.testbed.devices[stackpair["switch1"]].reload(timeout=600)
		except:
			time.sleep(120)
		self.testbed.devices[stackpair["switch1"]].disconnect()
		try:
			self.testbed.devices[stackpair["switch2"]].reload(timeout=600)
		except:
			time.sleep(120)
		self.testbed.devices[stackpair["switch2"]].disconnect()
		return True

	def configure_svl_step1(self, stackpair):

		config="""stackwise-virtual
					domain 2
				"""
		if not self.connect_to_stackpair(stackpair):
			Logger.error("Could not connect to devices, Can not proceed.")
			return False
		#On Switch1
		self.testbed.devices[stackpair["switch1"]].execute("switch 1 renumber  {}".format(
				self.testbed.devices[stackpair["switch1"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)
		self.testbed.devices[stackpair["switch1"]].execute("switch 2 renumber  {}".format(
				self.testbed.devices[stackpair["switch1"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)
		self.testbed.devices[stackpair["switch1"]].execute("switch {} priority 15".format(
				self.testbed.devices[stackpair["switch1"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)
		self.testbed.devices[stackpair["switch1"]].configure(config,reply=DIALOG_CONFIRM1)
		self.testbed.devices[stackpair["switch1"]].execute("show stackwise-virtual")
		#On Switch2
		self.testbed.devices[stackpair["switch2"]].execute("switch 1 renumber {}".format(
				self.testbed.devices[stackpair["switch2"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)
		self.testbed.devices[stackpair["switch2"]].execute("switch 2 renumber {}".format(
				self.testbed.devices[stackpair["switch2"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)

		self.testbed.devices[stackpair["switch2"]].execute("switch {} priority 10".format(
				self.testbed.devices[stackpair["switch2"]].custom["switchnumber"]),reply=DIALOG_CONFIRM)
		self.testbed.devices[stackpair["switch2"]].configure(config,reply=DIALOG_CONFIRM1)
		self.testbed.devices[stackpair["switch2"]].execute("show stackwise-virtual")

		return True

	def configure_svl_step2_svllinkconfig(self, stackpair):
		if not self.connect_to_stackpair(stackpair):
			Logger.error("Could not connect to devices, Can not proceed.")
			return False
		#On Switch1
		config1=""
		config2=""
		for link in self.testbed.devices[stackpair["switch1"]]:
			if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
				config1 += """
							interface {}
								stackwise-virtual link 1""".format(link.name)

		for link in self.testbed.devices[stackpair["switch2"]]:
			if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
				config2 += """
							interface {}
								stackwise-virtual link 1""".format(link.name)
		Logger.info(config1)
		Logger.info(config2)
		self.testbed.devices[stackpair["switch1"]].configure(config1)
		self.testbed.devices[stackpair["switch2"]].configure(config2)

		self.testbed.devices[stackpair["switch1"]].execute("show stackwise-virtual")
		self.testbed.devices[stackpair["switch2"]].execute("show stackwise-virtual")

		self.testbed.devices[stackpair["switch1"]].execute("write memory")
		self.testbed.devices[stackpair["switch2"]].execute("write memory")
		return True

	def configure_svl_step3_dad_linkconfig(self, stackpair):
		if not self.connect_to_stackpair(stackpair):
			Logger.error("Could not connect to devices, Can not proceed.")
			return False
		#On Switch1
		config1=""
		config2=""
		for link in self.testbed.devices[stackpair["switch1"]]:
			if link.link.name.upper().find('DAD-LINK') != -1:
				config1 += """interface {}
								stackwise-virtual dual-active-detection
								""".format(link.name)

		for link in self.testbed.devices[stackpair["switch2"]]:
			if link.link.name.upper().find('DAD-LINK') != -1:
				config2 += """interface {}
								stackwise-virtual dual-active-detection
								""".format(link.name)

		self.testbed.devices[stackpair["switch1"]].configure(config1)
		self.testbed.devices[stackpair["switch2"]].configure(config2)

		self.testbed.devices[stackpair["switch1"]].execute("show stackwise-virtual")
		self.testbed.devices[stackpair["switch2"]].execute("show stackwise-virtual")

		self.testbed.devices[stackpair["switch1"]].execute("write memory")
		self.testbed.devices[stackpair["switch2"]].execute("write memory")

		return True

	def disable_svl_config(self, stackpair):
		if not self.connect_to_stackpair(stackpair):
			Logger.error("Could not connect to devices, Can not proceed.")
			return False
		#On Switch1
		config1=""
		config2=""
		for link in self.testbed.devices[stackpair["switch1"]]:
			if link.link.name.lower().find('DAD-LINK') != -1:
				config1 += """interface {}
								no stackwise-virtual dual-active-detection""".format(link.name)

		for link in self.testbed.devices[stackpair["switch2"]]:
			if link.link.name.lower().find('DAD-LINK') != -1:
				config1 += """interface {}
								no stackwise-virtual dual-active-detection""".format(link.name)

		for link in self.testbed.devices[stackpair["switch1"]]:
			if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
				config1 += """
							interface {}
								no stackwise-virtual link 1""".format(link.name)

		for link in self.testbed.devices[stackpair["switch2"]]:
			if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
				config2 += """
							interface {}
								no stackwise-virtual link 1""".format(link.name)

		self.testbed.devices[stackpair["switch1"]].configure(config1)
		self.testbed.devices[stackpair["switch2"]].configure(config2)
		self.testbed.devices[stackpair["switch1"]].configure("no stackwise-virtual")
		self.testbed.devices[stackpair["switch2"]].configure("no stackwise-virtual")
		self.testbed.devices[stackpair["switch1"]].execute("write memory")
		self.testbed.devices[stackpair["switch2"]].execute("write memory")
		return True

	def configure_svl_step4_validate_svl(self,stackpair,retry=10):
		'''
		Validate the link status in the Stackwise Virtual
		'''
		result=True
		switches=[stackpair["switch1"], stackpair["switch2"]]
		dev_details=[]
		for dev in switches:
			output = self.testbed.devices[dev].execute("show stackwise-virtual")
			output1 = self.testbed.devices[dev].execute("show stackwise-virtual neighbors")
			output2 = self.testbed.devices[dev].execute("show stackwise-virtual dual-active-detection")
			if re.findall("Stackwise Virtual : Enabled", output):
				Logger.info("Stackwise Virtual Enabled")
			else:
				Logger.error("Stackwise Virtual not Enabled")
				result=False
			for link in self.testbed.devices[stackpair["switch1"]]:
				if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
					a=re.findall(link.name, output1)
					if len(a) >= 2:
						Logger.info("Link {} from switch {} is available in the links for stackwise Virtual!".format(link.name,stackpair["switch1"]))
					else:
						Logger.error("Link {} from switch {} is not available in the links for stackwise Virtual".format(link.name,stackpair["switch1"]))
						result=False
			for link in self.testbed.devices[stackpair["switch2"]]:
				if link.link.name.upper().find('STACKWISEVIRTUAL-LINK') != -1:
					a=re.findall(link.name, output1)
					if len(a) >= 2:
						Logger.info("Link {} from switch {} is available in the links for stackwise Virtual!".format(link.name,stackpair["switch2"]))
					else:
						Logger.error("Link {} from switch {} is not available in the links for stackwise Virtual".format(link.name,stackpair["switch2"]))
						result=False
			for link in self.testbed.devices[stackpair["switch1"]]:
				if link.link.name.upper().find('DAD-LINK') != -1:
					a=re.findall("\d+\s+{}\d+up".format(link.name), output2)
					if len(a) >= 2:
						Logger.info("Link {} from switch {} is available in DAD links!".format(link.name,stackpair["switch1"]))
					else:
						Logger.error("Link {} from switch {} is not available in DAD links!".format(link.name,stackpair["switch1"]))
						result=False
			for link in self.testbed.devices[stackpair["switch2"]]:
				if link.link.name.upper().find('DAD-LINK') != -1:
					a=re.findall("\d+\s+{}\d+up".format(link.name), output2)
					if len(a) >= 2:
						Logger.info("Link {} from switch {} is available in DAD links!!".format(link.name,stackpair["switch2"]))
					else:
						Logger.error("Link {} from switch {} is not available in DAD links!".format(link.name,stackpair["switch2"]))
						result=False
		if not result and retry > 0:
			time.sleep(30)
			return self.configure_svl_step4_validate_svl(stackpair,retry=retry-1)
		return result

	def check_stackwise_virtual_confgured(self,stackpair):
		'''
		Validate the link status in the Stackwise Virtual
		'''
		result=True
		switches=[stackpair["switch1"], stackpair["switch2"]]
		dev_details=[]
		for dev in switches:
			output1 = self.testbed.devices[dev].execute("show run | sec stackwise-virtual")
			if re.findall("stackwise-virtual", output1):
				Logger.info("Stackwise Virtual configs are present")
			else:
				Logger.error("Stackwise Virtual configs are not present on the switch: {}".format(dev))
				result=False
		return result

	def configure_svl(self, stackpair):
		#Validations
		'''
			Configure Stackwise SVL, All Steps in 1 functions good for multiple SVL config in parallel run
		'''
		if stackpair['switch1'] == stackpair['switch2']:
			Logger.error("The Device Pair has same name, invalid combination")
			return False

		if not self.check_links(stackpair):
			Logger.error("The devices provided to be paired into SVL does not have any links connected to eachothers")
			return False

		if not self.check_min_version_req(stackpair):
			Logger.info("Minimum Version check failed ")
			return False

		if not self.configure_svl_step1(stackpair):
			Logger.info("Step1 Config failed, Revover Mannuly.")
			return False
		self.save_config_and_reload(stackpair)

		if not self.configure_svl_step2_svllinkconfig(stackpair):
			Logger.info("Step1 Config failed, Revover Mannuly.")
			return False
		self.save_config_and_reload(stackpair)

		if not self.configure_svl_step3_dad_linkconfig(stackpair):
			Logger.info("Step1 Config failed, Revover Mannuly.")
			return False
		self.save_config_and_reload(stackpair)

		if not self.configure_svl_step4_validate_svl(stackpair):
			Logger.info("Step1 Config failed, Revover Mannuly.")
			return False

		return True


