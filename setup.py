from setuptools import setup

setup(name='topzemen',
	version='0.1.0-alpha',
	description='TopZemen',
	url='https://github.com/pronopython/topzemen',
	author='pronopython',
	author_email='pronopython@proton.me',
	license='GNU GENERAL PUBLIC LICENSE V3',
	packages=['topzemen'],
	package_data={'topzemen':['*']},
	include_package_data=True,
	zip_safe=False,
	install_requires=['Pillow'],
	entry_points={
		'gui_scripts': [
			'topzemen_no_cli=topzemen.topzemen:main',
			'zemenspawner_no_cli=topzemen.zemenspawner:main'
		],
		'console_scripts': [
			'topzemen=topzemen.topzemen:main',
			'zemenspawner=topzemen.zemenspawner:main',
			'printModuleDir_topzemen=topzemen.print_module_dir:printModuleDir'
		]
    	}
    )

