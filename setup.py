from setuptools import setup

setup(
    name='BedFileParser',
    version='1.0',
    packages=['data','BedFileParser','tests'],
    package_dir={'BedFileParser': 'BedFileParser'},
    url='',
    license='MIT',
    author='Sagar Chhangawala',
    author_email='sagarc88@gmail.com',
    description='',
    install_requires=['pandas'],
    test_suite='tests',
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'BedFileParser = BedFileParser.__main__:main'
        ]}
)
