import subprocess
import unittest
import os
import shutil
import datetime
import time
import sys
import argparse

INPUT_DIR_PATH = '../images'

TEST_CONFIGS = {
	'make': ('make', 'out', ['make'], False),
	'gradle': ('gradle', 'build', ['gradle.bat', 'thumb'], True),
	'doit': ('doit', 'out', ['.venv/Scripts/doit.exe'], True),
}

ROOT_DIR_PATH = ''
OUT_DIR_PATH = ''
BUILD_COMMAND = ''
CONTENT_BASED = False


class TestDeps(unittest.TestCase):

	def test_build_deps(self):
		# ---- Build from scratch, check files exist
		out_dir_path = OUT_DIR_PATH
		command = BUILD_COMMAND
		# Prepare
		os.chdir(ROOT_DIR_PATH)
		if os.path.exists(out_dir_path):
			shutil.rmtree(out_dir_path)
		
		out_png_dir_path = os.path.join(out_dir_path, 'thumb')
		self.png1_path = png1_path = os.path.join(out_png_dir_path, '1.png')
		self.png2_path = png2_path = os.path.join(out_png_dir_path, '2.png')
		self.files_txt_path = files_txt_path = os.path.join(out_dir_path, 'files.txt')
		
		self.update_timestamps(init=True)

		# Run
		subprocess.run(command, check=True)
		
		# Assert
		self.update_timestamps()
		self.assert_files_exist(out_png_dir_path, ['1.png', '2.png', '3.png'])
		self.assertTrue(os.path.isfile(files_txt_path))

		print('== Build from scratch OK')
		# ---- Remove files.txt - files.txt shall be regenerated
		# Sleep needed between make commands to make sure outdated timestamps can be detected
		if not CONTENT_BASED:
			time.sleep(1)
		
		os.remove(files_txt_path)
		
		subprocess.run(command, check=True)
		
		self.update_timestamps()
		self.assertEqual(self.png2_mtime, self.png2_prev_mtime)
		self.assertTrue(os.path.isfile(files_txt_path))

		print('== files.txt regen OK')
		# ---- Touch images/2.png -- only 2.png and files.txt shall be regenerated
		# TODO: test - touch out/2.png - only 2.png and files.txt are regenerated!
		if not CONTENT_BASED:
			time.sleep(1)

		png2_input_path = os.path.join(INPUT_DIR_PATH, '2.png')
		self.mod_file(png2_input_path)

		subprocess.run(command, check=True)

		self.update_timestamps()
		# png 1 shall not be regenerated
		self.assertEqual(self.png1_mtime, self.png1_prev_mtime, '1.png shall not be regenerated because only 2.png was changed')
		self.assertGreater(self.png2_mtime, self.png2_prev_mtime)
		self.assertGreater(self.filestxt_mtime, self.filestxt_prev_mtime)

		print('== touch top level .png regen OK')
		# ---- Touch files.txt - only files.txt shall be regenerated
		if not CONTENT_BASED:
			time.sleep(1)

		self.mod_file(files_txt_path)
		
		subprocess.run(command, check=True)

		self.update_timestamps()
		self.assertEqual(self.png1_mtime, self.png1_prev_mtime, '1.png shall not be regenerated because only files.txt was changed')
		self.assertGreater(self.filestxt_mtime, self.filestxt_prev_mtime)

		print('== touch files.txt regen OK')

	def update_timestamps(self, init=False):
		if not init:
			self.png1_prev_mtime = self.png1_mtime
			self.png2_prev_mtime = self.png2_mtime
			self.filestxt_prev_mtime = self.filestxt_mtime
		
		self.png1_mtime = None if init else os.path.getmtime(self.png1_path)
		self.png2_mtime = None if init else os.path.getmtime(self.png2_path)
		self.filestxt_mtime = None if init else os.path.getmtime(self.files_txt_path)

	def assert_files_exist(self, dir_path, file_names):
		for f in file_names:
			file_path = os.path.join(dir_path, f)
			self.assertTrue(os.path.isfile(file_path))

	def mod_file(self, file_path):
		if CONTENT_BASED:
			self.mod_bin(file_path)
		else:
			os.utime(file_path, None)

	def mod_bin(self, file_path):
		with open(file_path, 'ab') as file:
			file.write(bytearray([0x11, 0x11, 0x11, 0x11]))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('root', default='Root folder path')
	parser.add_argument('unittest_args', nargs='*')
	
	args = parser.parse_args()
	ROOT_DIR_PATH = args.root
	
	ROOT_DIR_PATH, OUT_DIR_PATH, BUILD_COMMAND, CONTENT_BASED = TEST_CONFIGS[args.root]
	
	# Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
	sys.argv[1:] = args.unittest_args
	unittest.main()
