from setuptools import setup, find_packages

setup(
    name="inventory-system",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl"
    ],
) 