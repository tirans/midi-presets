from setuptools import setup, find_packages

setup(
    name="midi-device-presets",
    version="2.1.0",
    description="A comprehensive system for managing MIDI device presets",
    author="tirans",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic[email]>=2.5.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0", 
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "validate-presets=midi_presets.cli.validate:ValidationCLI.run",
            "generate-checksums=midi_presets.cli.checksum:ChecksumCLI.run",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
