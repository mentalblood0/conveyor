from setuptools import setup, find_packages


if __name__ == '__main__':

	setup(
		name='conveyor',
		version='1.16.3',
		description='Library for creating cold-pipeline-oriented systems',
		long_description=open('README.md', encoding='utf-8').read(),
		long_description_content_type='text/markdown',
		author='mentalblood',
		install_requires=[
			'ring',
			'blake3',
			'peewee',
			'growing-tree-base',
			'pydantic',
			'psycopg2-binary'
		],
		packages=find_packages()
	)
