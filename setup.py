
from setuptools import setup, find_packages

setup(
    name="pyTLE9012DQU",
    version="0.9.0",
    description="A simple python library to control the Infineon TLE9012DQU BMS IC",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Markus Ekler",
    author_email="markus.ekler@web.de",
    url="https://github.com/maekdev/pyTLE9012DQU",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pyserial>=3.4",
    ],
)
