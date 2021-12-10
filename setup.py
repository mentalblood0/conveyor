import os
from distutils.core import setup



if __name__ == '__main__':

	long_description = ''
	if os.path.exists('README.md'):
		with open('README.md', encoding='utf-8') as f:
			long_description = f.read()

	setup(
		name='conveyor-mentalblood',
		version='0.2.0',
		description='Library for creating conveyor-oriented systems',
		long_description=long_description,
		long_description_content_type='text/markdown',
		author='mentalblood',
		install_requires=[
			'peewee',
			'growing-tree-base-mentalblood'
		],
		packages=[
			'conveyor', 
			'conveyor.providers',
			'conveyor.workers',
			'conveyor.workers.factories'
		]
	)