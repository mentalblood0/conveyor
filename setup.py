import pathlib
import setuptools



if __name__ == '__main__':

	packages = setuptools.find_packages(exclude = ['tests*'])

	setuptools.setup(
		name                          = 'conveyor',
		version                       = '2.2.7',
		description                   = 'Library for creating cold-pipeline-oriented systems',
		long_description              = (pathlib.Path(__file__).parent / 'README.md').read_text(),
		long_description_content_type = 'text/markdown',
		author                        = 'mentalblood',
		packages                      = packages,
		package_data                  = {
			name: ['py.typed']
			for name in packages
		},
		install_requires              = [
			'pydantic',
			'sqlalchemy'
		]
	)