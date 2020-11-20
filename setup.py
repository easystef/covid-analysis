import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

setup(
    name='local-covid19',
    version='1.1.0',
    description='Graphs Covid-19 data provided by the ECDC',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/easystef/covid-analysis',
    author='Stefan Hall',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=('tests', 'docs')),
    include_package_data=False,
    install_requires=['bokeh', 'pandas']
)