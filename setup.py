from setuptools import setup, find_packages

setup(
    name='name_com_dns',
    version='0.1',
    description='A script to run automatic dynamic DNS update of name.com DNS service, using their API.',
    author="Anders Fluur",
    author_email="your.email@example.com",
    url="https://github.com/AnderFluur/name_com_dns",
    packages=find_packages(),
    data_files=[('name_com_dns', ['name_com_dns/name_com_dns.service'])],
    install_requires=[
        'requests',
        'argparse',
        'configparser',
    ],
    entry_points={
        'console_scripts': [
            'name_com_dns=name_com_dns.name_dot_com_update:main',
        ],
    },
)