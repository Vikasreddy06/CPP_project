"""
Setup script for the campusfinder library.
Enables installation via: pip install -e .

Author: Vikas Reddy Amanagantti (x25178849)
"""

from setuptools import setup, find_packages

setup(
    name="campusfinder-vikasreddy",
    version="1.0.0",
    description="Custom OOP library for the Smart Campus Lost & Found System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vikas Reddy Amanagantti",
    author_email="Vikasreddy1510@gmail.com",
    url="https://github.com/Vikasreddy06/CPP_project",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
    ],
)
