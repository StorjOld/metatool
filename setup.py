from setuptools import setup

setup(
    name='metatool',
    version='1.0',
    packages=['metatool'],
    install_requires=[
        'requests',
        'btctxstore',
    ],
    test_suite='metatool.test_metadisk',
    entry_points={
        'console_scripts':
            ['metatool = metatool.metadisk:main']
    }
)
