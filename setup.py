from setuptools import find_packages, setup

setup(
    name='tasks',
    version='2.0.2',
    author='Paul Baecher',
    description='A simple personal task queue to track todo items',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/pb-/tasks',
    packages=find_packages(),
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'tasks = tasks.main:run',
        ],
    },
    scripts=[
        'scripts/tasks-i3status',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
