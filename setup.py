from setuptools import setup, find_packages

setup(
    name='metatool',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'btctxstore',
    ],
    include_package_data=True,
    test_suite='metatool',
    entry_points={
        'console_scripts':
            ['metatool = metatool.metadisk:main']
    }
)
