#!/usr/bin/env python3
"""
Setup script for TypeScript Playwright Cucumber Code Review Agent
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ts-playwright-cucumber-reviewer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered code review assistant for TypeScript, Playwright, and Cucumber projects",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ts-playwright-cucumber-reviewer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "linting": [
            "eslint",
            "prettier",
        ]
    },
    entry_points={
        "console_scripts": [
            "ts-reviewer=code_review_agent.cli:main",
            "ts-reviewer-server=code_review_agent.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "code_review_agent": [
            "standards/*.py",
            "templates/*.html",
            "config/*.json",
        ],
    },
    zip_safe=False,
)
