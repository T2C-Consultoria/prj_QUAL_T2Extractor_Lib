from setuptools import setup, find_packages

setup(
    name='t2extractor',
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "boto3==1.34.32",
        "openpyxl==3.1.2",
        "pandas==2.0.2",
        "pyodbc==4.0.38",
        "PyPDF2==2.11.1",
        "requests==2.31.0",
        "pdf2image==1.16.2",
    ],
)