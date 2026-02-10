#!/usr/bin/env python3
"""
SocialAI - Distraction-Free AI-Powered Social Media CLI
A modern CLI tool for consuming social media with AI intelligence
"""

from setuptools import setup, find_packages

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="socialai",
    version="1.0.0",
    author="Ali Zafar",
    author_email="support@socialai.dev",
    description="Distraction-free AI-powered social media CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AliZafar780/pc-control",
    project_urls={
        "Bug Reports": "https://github.com/AliZafar780/pc-control/issues",
        "Source": "https://github.com/AliZafar780/pc-control",
        "Documentation": "https://github.com/AliZafar780/pc-control/tree/main/docs",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.7.0"],
        "local": ["transformers>=4.30.0", "torch>=2.0.0"],
    },
    entry_points={
        "console_scripts": [
            "socialai=socialai.main:cli",
            "social=socialai.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "socialai": [
            "config/*.yaml",
            "data/*.db",
            "templates/*.html",
        ],
    },
    zip_safe=False,
    keywords="social-media, cli, ai, productivity, focus, distraction-free",
)
