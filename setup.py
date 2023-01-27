import pathlib
import setuptools



if __name__ == '__main__':

	setuptools.setup(
		name                          = 'conveyor',
		version                       = '2.0.0',
		description                   = 'Library for creating cold-pipeline-oriented systems',
		long_description              = (pathlib.Path(__file__).parent / 'README.md').read_text(),
		long_description_content_type = 'text/markdown',
		author                        = 'mentalblood',
		packages                      = setuptools.find_packages(exclude = ['tests*']),
		install_requires              = [
			'pydantic',
			'sqlalchemy'
		]
	)