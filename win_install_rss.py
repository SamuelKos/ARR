import sys
import pathlib
import subprocess
import os

tmp1 = 'create_scripts.bat'
tmp2 = 'install_rss.bat'

if sys.platform[:3] != 'win':
	print('This script is meant to be used on Windows only.')
	sys.exit(1)



temp1 = '''@echo off

set folder="venv"
py -m venv %folder% & %folder%\Scripts\\activate.bat & pip install wheel html2text & %folder%\Scripts\deactivate.bat'''


temp2 = '''@echo off
set folder="venv"

echo @echo off > rss.bat
echo cd %cd% >> rss.bat'''

temp3 ='''
echo venv\Scripts\\activate.bat ^& start /B "" "py" "arr.py" >> rss.bat
'''

fpath = pathlib.Path(tmp1)

if fpath.exists():
	print(f'\nCan not overwrite file: {fpath}')
else:
	try:
		with open(fpath, 'w', encoding='utf-8') as f:
			f.write(temp1)
		
	except EnvironmentError as e:
		print(e.__str__())
		print(f'\n Could not save file: {fpath}')



fpath = pathlib.Path(tmp2)

if fpath.exists():
	print(f'\nCan not overwrite file: {fpath}')
else:
	try:
		with open(fpath, 'w', encoding='utf-8') as f:
			f.write(temp2)
			f.write(temp3)
		
	except EnvironmentError as e:
		print(e.__str__())
		print(f'\n Could not save file: {fpath}')



try:
	subprocess.run(['install_rss.bat'])
	subprocess.run(['create_scripts.bat'])
	

	try:
		with open('rss.bat', 'r', encoding='utf-8') as f:
			tmp = f.read()
			fpath = pathlib.Path(sys.base_prefix) / 'rss.bat'

			with open(fpath, 'w', encoding='utf-8') as f2:
				f2.write(tmp)


	except EnvironmentError as e:
		print(e.__str__())
		print(f'\n Could not save file: {fpath}')
		
	os.remove('rss.bat')
	os.remove('create_scripts.bat')
	os.remove('install_rss.bat')
	print('\n\nRun with: rss')
	
except Exception as ee:
	print(ee)

























