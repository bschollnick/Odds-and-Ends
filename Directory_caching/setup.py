from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Directory_Caching',
    version='1.0.0',
    url='https://github.com/bschollnick/Odds-and-Ends',
    description = 'A Caching library for Directories & Files',
    author='Benjamin Schollnick',
    author_email='benjamin@schollnick.net',
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    keywords = ['caching', 'files', 'directories', 'scandir', 'naturalsort'], # arbitrary keywords
)
