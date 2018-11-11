from setuptools import setup, find_packages


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
)
