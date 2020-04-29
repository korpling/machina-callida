"""Setup file for easy installation of the application."""

# from distutils.core import setup
from setuptools import find_packages, setup

setup(
    # Application author details:
    author="Konstantin Schulz",
    author_email="konstantin.schulz@hu-berlin.de",

    # PyPi metadata
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"],

    # Summary of software purpose
    description="Backend with REST API for the CALLIDUS_HU project software",

    # Include additional files into the package
    include_package_data=True,

    # Dependent packages (distributions)
    # install_requires=[
    #     "Flask>=1.0.2", 'rapidjson>=1.0.0'
    # ],

    # License
    license_file="LICENSE",

    # more detailed information about the software
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",

    # Application name:
    name="mcserver",

    # Packages
    packages=find_packages(),  # ["app"],

    # Source Code
    url="https://scm.cms.hu-berlin.de/callidus/mc-backend",

    # Version number (initial):
    version="1.8.3",

    zip_safe=False, install_requires=['flask', 'graphannis']
)
