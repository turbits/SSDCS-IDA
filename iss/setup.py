from setuptools import setup

setup(
    name='iss',
    version='0.0.1',
    packages=['iss'],
    include_package_data=True,
    install_requires=[
        'flask==2.2.3',
        'cryptography==39.0.1',
        'python-dotenv==1.0.0',
        'requests==2.28.2'
    ]
)
