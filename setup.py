from setuptools import setup, find_packages

setup(
    name='namecom_dns',
    version='0.1',
    description='A script to run automatic dynamic DNS update of name.com DNS service, using their API.',
    long_description='''\
    This script allows you to update DNS records with the external IP address using the Name.com API.
    It periodically checks the external IP address and updates the DNS records accordingly.
    For detailed instructions and usage, please refer to the GitHub repository.
    ''',
    author="Anders Fluur",
    author_email="your.email@example.com",
    url="https://github.com/AnderFluur/namecom_dns",
    packages=find_packages(),
    data_files=[('namecom_dns', ['namecom_dns.service'])],
    install_requires=[
        'requests',
        'argparse',
        'configparser',
    ],
    entry_points={
        'console_scripts': [
            'namecom_dns=namecom_dns.namecom_update:main',
        ],
    },
)
