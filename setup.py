from setuptools import setup

setup(
    name='PyDrive',
    version='0.1.0',
    author='Joey Yakimowich-Payne',
    author_email='jyapayne@gmail.com',
    packages=['drivepy', 'drivepy.test'],
    url='https://github.com/jyapayne/DrivePy/',
    license='LICENSE',
    description='Pythonic Google Drive API Bindings.',
    long_description=open('README.md').read(),
    install_requires=[
        'google-api-python-client >= 1.5.0'
    ]
)
