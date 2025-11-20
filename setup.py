"""
Setup configuration for The17Project Instagram Content Automation

This file allows the package to be installed and distributed.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="the17project-automation",
    version="1.0.0",
    description="Automated Instagram content generation system for The17Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="The17Project",
    author_email="your-email@example.com",
    url="https://github.com/yourusername/the17project-automation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "openai>=1.12.0",
        "gspread>=5.12.0",
        "oauth2client>=4.1.3",
        "slack-sdk>=3.26.0",
        "python-dotenv>=1.0.0",
        "pytz>=2024.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "the17project=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="instagram automation content-generation openai google-sheets slack",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/the17project-automation/issues",
        "Source": "https://github.com/yourusername/the17project-automation",
    },
)
