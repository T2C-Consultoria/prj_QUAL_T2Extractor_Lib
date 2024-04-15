from setuptools import setup, find_packages

setup(
    name='t2extractor',
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.34.84",
        "openpyxl>=3.1.2",
        "pandas>=2.2.2",
        "pdf2image>=1.17.0",
        "pyodbc>=5.1.0",
        "PyPDF2>=3.0.1",
        "requests>=2.31.0",
    ],
)