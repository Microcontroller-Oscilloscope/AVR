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

import os

def listConfigs() -> list[str]:
	"""
	Gets list of available configurations\n
	:return list of configuration names
	"""

	configPath = "nbproject/configurations.xml"

	if not os.path.exists(configPath):
		print("Configuration path: '" + configPath + "' doesn't exist!")
		exit(-1)
	
	configFile = open(configPath, "r")

	configNames:list[str] = []

	try:
		lines = configFile.readlines()

		for line in lines:
			if line.find("<conf name=") != -1:
				# found config name
				startIndex = line.find("\"") + 1
				endIndex = line.find("\"", startIndex)

				configNames.append(line[startIndex:endIndex])

		configFile.close()

	except (BlockingIOError, OSError, ValueError):
		print("Failed to read lines for " + configPath)

	return configNames

def getConfig() -> str:
	"""
	Gets name of current configuration\n
	:return	configuration name
	"""

	return ""

def writeConfig(path: str, keyStr: str, endStr: str, fillerStr: str):
	"""
	Updates selected config of project\n
	:param path			value to print\n
	:param keyStr		str to check to modify line\n
	:param endStr		end of str to modify\n
	:param fillerStr	str to replace file
	"""

	configurationFile = open(path, "r")
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
	configurationFile = open(path, "w")
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

	while True:
		try:
			chosenIndex = int(input(""))
			if chosenIndex >= 0 and chosenIndex < len(configs):
				break
		except:
			next

	writeConfig("nbproject/private/configurations.xml", "<defaultConf>", "<", str(chosenIndex))
	writeConfig("nbproject/Makefile-impl.mk", "DEFAULTCONF=", "\n", configs[chosenIndex])

def getBoard() -> str:
	"""
	Gets board selected for configuration\n
	:return name of board
	"""
	return "ATmega328P"

def getPort() -> str:
	"""
	Gets port of connected board\n
	:return port name
	"""
	#ls /dev/tty*
	return "/dev/ttyACM0"

def getBuildPath() -> str:
	"""
	Gets path for build files\n
	:return build path
	"""
	return "dist/default/production/"

def uploadApp():
	"""
	Uploads application to target board
	"""
	os.system("make")
	os.system("avrdude -p " + getBoard() + " -c arduino -P " + getPort() + " -U flash:w:" + getBuildPath() + "AVR.production.hex:i")

if __name__ == '__main__':
	#uploadApp()
	setConfig()