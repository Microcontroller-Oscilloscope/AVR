"""
	uploader.py - uploads firmware to avr board
	Copyright (C) 2025 Camren Chraplak

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from io import TextIOWrapper
import os
import platform
import subprocess
import sys

publicConfigPath = "nbproject/configurations.xml"
""" public configurations file for project """

privateConfigPath = "nbproject/private/configurations.xml"
""" private configurations file for user """

makeImpPath = "nbproject/Makefile-impl.mk"
""" configuration for compiling project """

def openReadFile(path: str) -> TextIOWrapper:
	"""
	Opens path file in read mode\n
	:param	path file path to open\n
	:return open file
	"""

	if not os.path.exists(path):
		print("Path: '" + path + "' doesn't exist!")
		exit(-1)
	
	return open(path, "r")

def openWriteFile(path: str) -> TextIOWrapper:
	"""
	Opens path file in write mode\n
	:param	path file path to open\n
	:return open file
	"""

	if not os.path.exists(path):
		print("Path: '" + path + "' doesn't exist!")
		exit(-1)
	
	return open(path, "w")

def listConfigs() -> list[str]:
	"""
	Gets list of available configurations\n
	:return list of configuration names
	"""

	configFile = openReadFile(publicConfigPath)
	configNames:list[str] = []

	try:
		lines = configFile.readlines()

		for line in lines:
			if line.find("<conf name=") != -1:
				# found config name
				startIndex = line.find("\"") + 1
				endIndex = line.find("\"", startIndex)

				configNames.append(line[startIndex:endIndex])

	except (BlockingIOError, OSError, ValueError):
		print("Failed to read lines for " + publicConfigPath)
	
	configFile.close()

	return configNames

def getConfigIndex() -> int:
	"""
	Gets index of current configuration\n
	:return	configuration index
	"""

	configFile = openReadFile(privateConfigPath)

	try:
		lines = configFile.readlines()

		for line in lines:
			if line.find("<defaultConf>") != -1:
				startIndex = line.find(">") + 1
				endIndex = line.find("<", startIndex)
				configFile.close()
				return int(line[startIndex:endIndex])

	except (BlockingIOError, OSError, ValueError):
		print("Failed to read lines for " + privateConfigPath)
	
	configFile.close()
	exit(-1)

	return 0

def getConfig() -> str:
	"""
	Gets name of current configuration\n
	:return	configuration name
	"""

	return listConfigs()[getConfigIndex()]

def writeConfig(path: str, keyStr: str, endStr: str, fillerStr: str):
	"""
	Updates selected config of project\n
	:param path			value to print\n
	:param keyStr		str to check to modify line\n
	:param endStr		end of str to modify\n
	:param fillerStr	str to replace file
	"""

	configurationFile = openReadFile(path)
	configurationLines = configurationFile.readlines()
	i = 0

	# reads and stores lines
	for line in configurationLines:
		if line.find(keyStr) != -1:
			startIndex = line.find(keyStr[-1]) + 1
			endIndex = line.find(endStr, startIndex)
			configurationLines[i] = line[:startIndex] + fillerStr + line[endIndex:]
		i += 1

	configurationFile.close()
	configurationFile = openWriteFile(path)
	i = 0

	# writes original and modified lines
	for line in configurationLines:
		configurationFile.write(configurationLines[i])
		i += 1
	
	configurationFile.close()

def setConfig():
	"""
	Sets configuration environment of project
	"""

	configs = listConfigs()

	print("choose config:")

	for config in range(len(configs)):
		print("\t" + str(config) + ": " + configs[config])
	
	chosenIndex: int

	try:
		chosenIndex = int(input(""))
		if chosenIndex < 0 or chosenIndex >= len(configs):
			print("Invalid input")
			return
	except:
		print("Invalid input")
		return

	writeConfig(privateConfigPath, "<defaultConf>", "<", str(chosenIndex))
	writeConfig(makeImpPath, "DEFAULTCONF=", "\n", configs[chosenIndex])

def getBoard() -> str:
	"""
	Gets board selected for configuration\n
	:return name of board
	"""

	configFile = openReadFile(publicConfigPath)

	prevConfigName = ""
	configName = getConfig()

	try:
		lines = configFile.readlines()

		for line in lines:

			# gets selected config
			if line.find("<conf name=") != -1:
				startIndex = line.find("\"") + 1
				endIndex = line.find("\"", startIndex)
				prevConfigName = line[startIndex:endIndex]
			
			# gets selected device
			if line.find("<targetDevice>") != -1 and prevConfigName == configName:
				startIndex = line.find(">") + 1
				endIndex = line.find("<", startIndex)
				return line[startIndex:endIndex]

	except (BlockingIOError, OSError, ValueError):
		print("Failed to read lines for " + publicConfigPath)
	
	configFile.close()

	return ""

def getPorts() -> list[str]:
	"""
	Gets port of connected board\n
	:return port name
	"""

	command = ""
	excludeStr: list[str] = []
	excludeExact: list[str] = ["\n"]

	if platform.system() == "Linux":
		command = "ls /dev/tty*"

		# Linux excludes
		excludeStr.append("ttyS")
		excludeStr.append("ttyprintk")
		for i in range(10):
			excludeStr.append("tty" + str(i))
		
		excludeExact.append("/dev/tty")
	# TODO: add more operating systems
	else:
		print("OS not supported, exiting...")
		exit(-1)
	
	allPorts = subprocess.check_output(command, shell=True, text=True).splitlines()
	ports: list[str] = []

	for port in allPorts:
		
		validPort = True

		# checks if port is valid
		for excStr in excludeStr:
			if port.find(excStr) != -1:
				validPort = False
		for exaStr in excludeExact:
			if exaStr == port:
				validPort = False

		if validPort:
			ports.append(port)

	return ports

def uploadApp():
	"""
	Uploads application to target board
	"""
	os.system("make")

	ports = getPorts()
	for port in ports:
		os.system("avrdude -p " + getBoard() + " -c arduino -P " + port + " -U flash:w:dist/" + getConfig() + "/production/AVR.production.hex:i")

	if len(ports) == 0:
		print("No valid ports found")

def printHelp():
	"""
	Prints help for running commands
	"""
	runCommand = "python3 uploader.py"
	print("Valid commands (flags can be upper or lower case):")
	print("\t" + runCommand)
	print("\t\tCompiles and uploads selected config to board")
	print("\t" + runCommand + " -c")
	print("\t\tSets configuration of project")

if __name__ == '__main__':

	if len(sys.argv) <= 1:
		uploadApp()
	elif len(sys.argv) == 2:
		arg = sys.argv[1]
		if arg == "-C" or arg == "-c":
			setConfig()
		else:
			printHelp()
	else:
		printHelp()