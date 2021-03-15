from conans import ConanFile
from conans import tools
from conan.tools.cmake import CMake
from os.path import join
import os
import re
import subprocess
import tarfile
import shutil
import sys

class ArmNoneEabiGccConan(ConanFile):
	name = "arm-none-eabi-gcc"
	license = "GNU-GPLv3"
	description = "ARM crosscompiler for cortex-A, cortex-M, and cortex-R"
	settings = "os", "arch", "compiler", "build_type"
	archiveName = "gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2"

	# version must match arm-none-eabi-gcc binary
	version = "10.2.1"
	_forceExtract = False
	_extractDir = "extract"
	
	# ARM's versioning in the file names does not match the gcc version, so we need a list of versions
	_archiveName = {
		"9.3.1":	"gcc-arm-none-eabi-9-2020-q2-update-x86_64-linux.tar.bz2",
		"10.2.1":	"gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2"
	}
	exports_sources = _archiveName[version]

	def _getExtractPath(self):
		extractPath = join(self._extractDir, os.listdir("./extract")[0])
		return(extractPath)

	def source(self):
		# extract archive
		if(self._forceExtract == True or os.path.isdir(self._extractDir) == False):
			print("Extracting toolchain archive...")
			shutil.rmtree(self._extractDir, ignore_errors=True)
			tar = tarfile.open(self._archiveName[self.version], "r:bz2")
			tar.extractall(path="extract")
			tar.close()
		else:
			print("Skipping toolchain archive extraction")

		# verify version number from gcc
		extractPath = self._getExtractPath()
		cmd = join(extractPath, "bin", "arm-none-eabi-gcc") + " -dumpversion"
		result = subprocess.check_output(cmd, shell=True).decode('ASCII') 
		result = re.search(r"^\S*", result).group(0)
		if(result != self.version):
			print("arm-none-eabi-gcc version: ", result, sep='')
			print("expected version:          ", self.version, sep='')
			sys.exit("Version of gcc does not match artifact version")
		
	def package(self):
		# repackage resources
		extractPath = self._getExtractPath()
		self.copy("arm-none-eabi/*",	src=extractPath,	keep_path=True)
		self.copy("bin/*",				src=extractPath,	keep_path=True)
		self.copy("lib/*",				src=extractPath,	keep_path=True)
		self.copy("share/doc/gcc-arm-none-eabi/license.txt", src=extractPath, dst="licenses", keep_path=False)

	def package_info(self):	
		dir_pkg = self.package_folder
		dir_bin = join(dir_pkg, "bin")
		#dir_sysroot = join(dir_pkg, "arm-none-eabi")

		# lib search path
		self.cpp_info.libdirs = ["arm-none-eabi/lib"]
		self.cpp_info.includedirs = ["arm-none-eabi/include"]

		# add binaries to PATH
		self.env_info.path.append(dir_bin)

		# set env vars
		self.env_info.AR		= join(dir_bin, "arm-none-eabi-ar")
		self.env_info.CC		= join(dir_bin, "arm-none-eabi-gcc")
		self.env_info.CPP		= join(dir_bin, "arm-none-eabi-cpp")
		self.env_info.CXX		= join(dir_bin, "arm-none-eabi-g++")
		self.env_info.RANLIB 	= join(dir_bin, "arm-none-eabi-gcc-ranlib")
		self.env_info.STRIP		= join(dir_bin, "arm-none-eabi-strip")
		#self.env_info.CONAN_CMAKE_SYSROOT	= dir_sysroot
		


