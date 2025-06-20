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
        # Core optimization libraries
        "ortools>=9.7.2963",
        "mip>=1.15.0",
        "pulp>=2.7.0",
        "scipy>=1.11.0",
        "numpy>=1.24.0",
        
        # Data processing & visualization
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        
        # Performance
        "numba>=0.57.0",
        "joblib>=1.3.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
        "reporting": [
            "openpyxl>=3.1.0",
            "xlsxwriter>=3.1.0",
            "plotly>=5.15.0",
        ],
        "advanced": [
            "cvxpy>=1.4.0",
            "networkx>=3.1",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "all": [
            "openpyxl>=3.1.0",
            "xlsxwriter>=3.1.0",
            "plotly>=5.15.0",
            "cvxpy>=1.4.0",
            "networkx>=3.1",
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    keywords="cutting-stock, optimization, 2d-cutting, manufacturing, algorithms",
    project_urls={
        "Bug Reports": "https://github.com/gastonfr24/surface-cutting-optimizer/issues",
        "Source": "https://github.com/gastonfr24/surface-cutting-optimizer",
        "Documentation": "https://github.com/gastonfr24/surface-cutting-optimizer/docs",
    },
) 