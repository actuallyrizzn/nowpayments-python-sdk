from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nowpayments-python-sdk",
    version="1.0.0",
    author="NOWPayments SDK Team",
    author_email="support@nowpayments.io",
    description="Official Python SDK for NOWPayments API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nowpayments/nowpayments-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pyjwt>=2.0.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
    },
    keywords="nowpayments, cryptocurrency, payments, api, sdk",
    project_urls={
        "Bug Reports": "https://github.com/nowpayments/nowpayments-python-sdk/issues",
        "Source": "https://github.com/nowpayments/nowpayments-python-sdk",
        "Documentation": "https://nowpayments.io/docs",
    },
) 