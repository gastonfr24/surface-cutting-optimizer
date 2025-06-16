from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="surface-cutting-optimizer",
    version="1.0.0-beta",
    author="Surface Cutting Team", 
    author_email="team@surfacecutting.com",
    description="Librería para optimización de corte de superficies bidimensionales",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/surface-cutting-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0", 
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "shapely>=1.8.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910"
        ],
        "viz": [
            "plotly>=5.0",
            "pillow>=8.3.0",
            "seaborn>=0.11.0"
        ],
        "advanced": [
            "numba>=0.56",
            "deap>=1.3",
            "scikit-learn>=1.0"
        ],
        "export": [
            "reportlab>=3.6.0",
            "svglib>=1.2.0",
            "cairosvg>=2.5.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "surface-optimizer=surface_optimizer.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "cutting stock problem", 
        "bin packing", 
        "optimization", 
        "2d cutting", 
        "material optimization",
        "manufacturing",
        "glass cutting",
        "metal cutting", 
        "wood cutting",
        "fabric cutting"
    ]
) 