import time
import subprocess

def main():
	action = prompt_user_for_valid_input("(C)onnect or (R)econnect a device?", ("C", "R"))
	
	if action == "R":
		devices = get_paired_devices()
		show_devices(devices)
		device_num = prompt_user_for_device_number("Type the number of the device you want to reset: ")
		mac_addr = devices[device_num-1].get("mac_address")
	
		untrust_device(mac_addr)
		remove_device(mac_addr)

	input("Set device to pairing mode, then press enter.")

	if action == "C":
		devices = scan_devices()
		if len(devices) >= 1:
			show_devices(devices)
			device_num = prompt_user_for_device_number("Type the number of the device you want to connnect: ")
			mac_addr = devices[device_num-1].get("mac_address")
		else:
			print("Ne Devices Found")
			exit(1)
		
	activate_agent()
	
	is_device_found = scan_for_device(mac_addr)
	if is_device_found:
		trust_device(mac_addr)
		pair_device(mac_addr)
		connect_device(mac_addr)
	else:
		"Device not found."


def get_devices():
	print(f"get_devices()")
	ctl_str = 'bluetoothctl'
	devices_str = "devices"
	
	stream = subprocess.run([ctl_str, devices_str], stdout = subprocess.PIPE)
	output = stream.stdout.decode("utf-8").split("\n")

	devices = []
	for line in output:
		if line:
			device = line.split(' ', 2)
			device = {
				"mac_address" : device[1],
				"name" : device[2],
			}
			devices.append(device)
	return devices


def get_paired_devices():
	ctl_str = 'bluetoothctl'
	devices_str = "paired-devices"
		
	stream = subprocess.run([ctl_str, devices_str], stdout = subprocess.PIPE)
	output = stream.stdout.decode("utf-8").split("\n")

	devices = []
	for line in output:
		if line:
			device = line.split(' ', 2)
			device = {
				"mac_address" : device[1],
				"name" : device[2],
			}
			devices.append(device)
	return devices


def show_devices(devices):
	print("\nList of Bluetooth devices:\n")
	print("NUMBER\tMAC ADDRESS\t\tDEVICE NAME")
	for count, value in enumerate(devices, start=1):
		print(f"{count}\t{value.get('mac_address')}\t{value.get('name')}")
	print()


def prompt_user_for_valid_input(prompt_message, valid_inputs):
	if not (user_response := input(prompt_message)):
		pass
	else:
		if user_response.upper() not in valid_inputs:
			pass
		else:
			return user_response.upper()
	return prompt_user_for_valid_input(prompt_message, valid_inputs)

def prompt_user_for_device_number(message):
	if not (device_num := input(message)):
		pass
	else:
		if not device_num.isdecimal():
			pass
		else:
			return int(device_num)
	return prompt_user_for_device_number()


def untrust_device(mac_addr):
	if __debug__: 
		print(f"Removing MAC address {mac_addr} from the trusted Bluetooth device list.")
	ctl_str = 'bluetoothctl'
	untrust_str = "untrust"
	
	stream = subprocess.run(
		[ctl_str, untrust_str, str(mac_addr)], 
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)

	if __debug__:
		output = stream.stdout.decode("utf-8")
		lines = output.split("\n")
		for line in lines:
			print(line, end="\r")
		print()
	
	if stream.returncode == 1:
		raise ValueError(f"error: untrust_device({mac_addr}) - {stream.stderr}")

	# print(f"Changing {mac_addr} untrust succeeded.")
	return stream.returncode


def trust_device(mac_addr):
	if __debug__: 
		print(f"Adding MAC address {mac_addr} to the trusted Bluetooth device list.")
	ctl_str = 'bluetoothctl'
	trust_str = "trust"
	
	stream = subprocess.run(
		[ctl_str, trust_str, str(mac_addr)], 
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)
	if __debug__:
		output = stream.stdout.decode("utf-8")
		lines = output.split("\n")
		for line in lines:
			print(line, end="\r")
	print()
	print()

	if stream.returncode == 1:
		raise ValueError(f"error: trust_device({mac_addr}) - {stream.stderr}")
	
	return stream.returncode
	

def remove_device(mac_addr):
	if __debug__:
		print(f"Removing MAC address {mac_addr} from the Bluetooth device list.")
	ctl_str = 'bluetoothctl'
	remove_str = "remove"
	
	stream = subprocess.run(
		[ctl_str, remove_str, str(mac_addr)],
		stdout = subprocess.PIPE, 
		stderr = subprocess.PIPE
	)
	if __debug__:
		output = stream.stdout.decode("utf-8")
		lines = output.split("\n")
		for line in lines:
			print(line, end="\r")
		print()

	if stream.returncode == 1:
		raise ValueError(f"error: remove_device({mac_addr}) - {stream.stderr}")
	
	return stream.returncode


def pair_device(mac_addr):
	ctl_str = 'bluetoothctl'
	pair_str = "pair"
	
	# stream = subprocess.run(
	# 	[ctl_str, pair_str, str(mac_addr)],
	# 	stdout = subprocess.PIPE, 
	# 	stderr = subprocess.PIPE
	# )

	process = subprocess.Popen(
		[ctl_str, pair_str, str(mac_addr)],
		stdout = subprocess.PIPE,
		stdin = subprocess.PIPE,
		stderr = subprocess.PIPE,
		universal_newlines=True,
		bufsize=0,
		text=True,
	)

	while process.poll() is None:
		output = process.stdout.readline()
		lines = output.split("\n")
		for line in lines:
			print(f"\t{line}", end="\r")

	# if __debug__:
	# 	output = stream.stdout.decode("utf-8")
	# 	lines = output.split("\n")
	# 	for line in lines:
	# 		print(line, end="\r")
	print()

	if process.returncode == 1:
		raise ValueError(f"error: pair_device({mac_addr}) - {process.stderr}")
	
	return process.returncode


def connect_device(mac_addr):
	print(f"Connecting to the device with a MAC address {mac_addr}.")
	ctl_str = 'bluetoothctl'
	connect_str = "connect"
	
	stream = subprocess.run(
		[ctl_str, connect_str, str(mac_addr)],
		stdout = subprocess.PIPE, 
		stderr = subprocess.PIPE
	)
	if __debug__:
		output = stream.stdout.decode("utf-8")
		lines = output.split("\n")
		for line in lines:
			print(line, end="\r")
		print()

	if stream.returncode == 1:
		raise ValueError(f"error: connect_device({mac_addr}) - {stream.stderr}")
	
	return stream.returncode


def activate_agent():
	print(f"Activating the Bluetoothctl agent.")
	ctl_str = 'bluetoothctl'
	agent_str = "agent"
	on_str = "on"
	
	stream = subprocess.run(
		[ctl_str, agent_str, on_str],
		stdout = subprocess.PIPE, 
		stderr = subprocess.PIPE
	)
	output = stream.stdout.decode("utf-8")
	print(output)

	if stream.returncode == 1:
		raise ValueError(f"error: activate_agent() - {stream.stderr}")
	
	return stream.returncode


def get_mac_addr():
	print(f"get_mac_addr()")
	ctl_str = 'hcitool'
	scan_str = "scan"
	
	stream = subprocess.run(
		[ctl_str, scan_str],
		stdout = subprocess.PIPE, 
		stderr = subprocess.PIPE
	)

	output = stream.stdout.decode("utf-8")
	print(output)

	if stream.returncode == 1:
		raise ValueError(f"error: activate_agent() - {stream.stderr}")
	
	return stream.returncode


def scan_devices():
	print(f"Scanning for devices in pairing mode.")
	ctl_str = 'hcitool'
	scan_str = "scan"
	process = subprocess.Popen(
		[ctl_str, scan_str],
		stdout = subprocess.PIPE,
		stdin = subprocess.PIPE,
		stderr = subprocess.PIPE,
		universal_newlines=True,
		bufsize=0,
		text=True,
	)
	
	timeout_duration = 30
	timeout = time.time() + timeout_duration
	
	devices = []
	while process.poll() is None:
		output = process.stdout.readlines()
		for line in output:
			if line.startswith("\t"):
				mac_addr, name = line.strip().split('\t')
				device = {
					"mac_address" : mac_addr,
					"name" : name,
				}
				devices.append(device)

		if time.time() > timeout:
			print("TIMEOUT")
			break
	
	return devices


def scan_for_device(mac_addr):
	print(f"Scanning for a device with a MAC address {mac_addr}.")
	ctl_str = 'bluetoothctl'
	process = subprocess.Popen(
		[ctl_str],
		stdout = subprocess.PIPE,
		stdin = subprocess.PIPE,
		stderr = subprocess.PIPE,
		universal_newlines=True,
		bufsize=0,
		text=True,
	)
	
	#####
	# Start Bluetooth Scanning
	###
	process.stdin.write("scan on\n")
	
	#####
	# Look for mac_addr
	###
	mac_is_found = False
	
	timeout_duration = 10
	timeout = time.time() + timeout_duration

	while process.poll() is None:
		output = process.stdout.readline()
		
		if __debug__:
			lines = output.split("\n")
			for line in lines:
				print(f"\t{line}", end="\r")

		if output.find(str(mac_addr)) != -1:
			mac_is_found = True
			break

		if time.time() > timeout:
			break
	
	print()
	print()

	#####
	# Stop Bluetooth Scanning
	###
	process.stdin.write("scan off\n")

	if process.returncode == 1:
		print(f"scan_for_device({mac_addr})")
		print(f"\t{process.stderr}")
		exit(1)
	if not mac_is_found:
		return False
	
	return True
	
	


if __name__ == "__main__":
	main()