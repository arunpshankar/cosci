from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-cosci",
    version="0.1.1",
    author="Co-Scientist Team",
    author_email="coscientist@example.com",
    description="Python SDK for Google's Co-Scientist",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arunpshankar/cosci.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
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
        "requests>=2.28.0",
        "google-auth>=2.16.0",
        "google-auth-oauthlib>=0.4.6",
        "google-auth-httplib2>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.990",
            "twine>=4.0",
            "build>=0.9",
        ],
        "colors": [
            "colorama>=0.4.4",
        ],
    },
)
