from setuptools import setup

setup(
    name='pyflock',
    version='0.1.0',
    description='Pytest plugin for sending notifications about completed test runs',
    url='https://www.pyflock.com',
    author='Andrey Letenkov',
    author_email='andletenkov@gmail.com',
    license='proprietary',
    py_modules=['api', 'pyflock'],
    install_requires=['pytest', 'requests'],
    entry_points={'pytest11': ['pyflock = pyflock', ], },
)
