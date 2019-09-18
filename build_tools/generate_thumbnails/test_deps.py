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
	'gradle': ('gradle', 'build', ['gradlew.bat', 'thumb'], True),
	'doit': ('doit', 'out', ['.venv/Scripts/doit.exe'], True),
}

ROOT_DIR_PATH = ''
OUT_DIR_PATH = ''
BUILD_COMMAND = ''
CONTENT_BASED = False


class TestDeps(unittest.TestCase):

	def test_build_deps(self):
		# ---- Build from scratch, check files exist (scratch)
		out_dir_path = OUT_DIR_PATH
		command = BUILD_COMMAND
		# Prepare
		os.chdir(ROOT_DIR_PATH)
		if os.path.exists(out_dir_path):
			shutil.rmtree(out_dir_path)
		
		# Run
		subprocess.run(command, check=True)
		
		# Assert
		out_png_dir_path = os.path.join(out_dir_path, 'thumb')
		png1_path = os.path.join(out_png_dir_path, '1.png')
		png2_path = os.path.join(out_png_dir_path, '2.png')
		self.assert_files_exist(out_png_dir_path, ['1.png', '2.png', '3.png'])

		files_txt_path = os.path.join(out_dir_path, 'files.txt')
		self.assertTrue(os.path.isfile(files_txt_path))

		png2_prev_mtime = os.path.getmtime(png2_path)

		print('== Build from scratch OK')

		# ---- Remove files.txt - only files.txt shall be regenerated (down)
		# Sleep needed between make commands to make sure outdated timestamps can be detected
		time.sleep(1)
		os.remove(files_txt_path)
		
		subprocess.run(command, check=True)
		
		png2_mtime = os.path.getmtime(png2_path)
		self.assertEqual(png2_mtime, png2_prev_mtime)
		self.assertTrue(os.path.isfile(files_txt_path))

		png2_prev_mtime = png2_mtime

		print('== files.txt regen OK')
		
		time.sleep(1)

		png2_input_path = os.path.join(INPUT_DIR_PATH, '2.png')
		os.utime(png2_input_path, None)

		subprocess.run(command, check=True)

		png2_mtime = os.path.getmtime(png2_path)
		self.assertGreater(png2_mtime, png2_prev_mtime)

		filestxt_prev_mtime = os.path.getmtime(files_txt_path)

		print('== touch top level .png regen OK')

		time.sleep(1)

		os.utime(png2_path, None)
		
		subprocess.run(command, check=True)

		filestxt_mtime = os.path.getmtime(files_txt_path)
		if not CONTENT_BASED:
			self.assertGreater(filestxt_mtime, filestxt_prev_mtime)
		# else: TODO: alter file for content based engines
		
		png1_prev_mtime = os.path.getmtime(png1_path)
		filestxt_prev_mtime = filestxt_mtime

		print('== touch files.txt regen OK')

		time.sleep(1)
		# ---- Remove input file 2.png, files.txt shall be regenerated (up)
		os.remove(png2_path)
		subprocess.run(command, check=True)
		
		png1_mtime = os.path.getmtime(png1_path)
		# png 1 shall not be regenerated
		self.assertEqual(png1_mtime, png1_prev_mtime)

		# png 2 shall be generated
		self.assertTrue(os.path.isfile(png2_path))
		
		# files.txt shall be regenerated
		filestxt_mtime = os.path.getmtime(files_txt_path)
		self.assertGreater(filestxt_mtime, filestxt_prev_mtime)
		
		print('== only png 2 regen OK')

	def assert_files_exist(self, dir_path, file_names):
		for f in file_names:
			file_path = os.path.join(dir_path, f)
			self.assertTrue(os.path.isfile(file_path))


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
