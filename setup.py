#!/usr/bin/env python3
"""
Biomedical Data Extraction Engine
A comprehensive system for extracting structured patient-level data from biomedical literature.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="biomedical-extraction-engine",
    version="1.0.0",
    author="Manus AI",
    author_email="contact@manus.ai",
    description="A comprehensive system for extracting structured patient-level data from biomedical literature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/manus-ai/biomedical-extraction-engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "gpu": [
            "torch>=2.1.0+cu118",
            "torchvision>=0.16.0+cu118",
            "torchaudio>=2.1.0+cu118",
        ],
        "all": [
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
            "plotly>=5.17.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "biomedical-extract=core.cli:main",
            "biomedical-server=api.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
    },
    zip_safe=False,
)

