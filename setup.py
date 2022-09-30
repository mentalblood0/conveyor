import os
from setuptools import setup, find_packages


if __name__ == '__main__':

	long_description = ''
	if os.path.exists('README.md'):
		with open('README.md', encoding='utf-8') as f:
			long_description = f.read()

	setup(
		name='conveyor',
		version='1.14.0',
		description='Library for creating cold-pipeline-oriented systems',
		long_description=long_description,
		long_description_content_type='text/markdown',
		author='mentalblood',
		install_requires=[
			'ring',
			'blake3',
			'peewee',
			'growing-tree-base',
			'pydantic'
		],
		packages=find_packages()
	)
