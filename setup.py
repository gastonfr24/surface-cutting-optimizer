#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="surface-cutting-optimizer",
    version="1.0.0-beta",
    author="Surface Cutting Optimizer Team",
    author_email="gastonfr24@gmail.com",
    description="Advanced library for bidimensional surface cutting optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gastonfr24/surface-cutting-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "pandas>=1.1.0",
        "dataclasses-json>=0.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
        "reporting": [
            "openpyxl>=3.0.0",
            "jinja2>=2.11.0",
            "weasyprint>=52.0",
        ],
        "visualization": [
            "plotly>=4.14.0",
            "dash>=1.19.0",
        ],
        "all": [
            "openpyxl>=3.0.0",
            "jinja2>=2.11.0", 
            "weasyprint>=52.0",
            "plotly>=4.14.0",
            "dash>=1.19.0",
        ],
    },
    keywords="cutting-stock, optimization, 2d-cutting, manufacturing, algorithms",
    project_urls={
        "Bug Reports": "https://github.com/gastonfr24/surface-cutting-optimizer/issues",
        "Source": "https://github.com/gastonfr24/surface-cutting-optimizer",
        "Documentation": "https://github.com/gastonfr24/surface-cutting-optimizer/docs",
    },
) 