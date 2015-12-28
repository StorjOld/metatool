from setuptools import setup


required_packages = ['requests', 'btctxstore']

setup(
    name='metatool',
    version='1.0',
    packages=['metatool'],
    install_requires=required_packages,
    test_suite='metatool.tests',
    entry_points={
        'console_scripts':
            ['metatool = metatool.__main__:main']
    }
)
