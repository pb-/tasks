from setuptools import find_packages, setup

setup(
    name='tasks',
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
)
