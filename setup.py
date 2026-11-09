from setuptools import setup, find_packages

setup(
    name="qnx-sentinel",
    version="1.0.0",
    author="QNX Sentinel Hackathon Engineering Team",
    description="Intelligent QNX 8.0 Build, Test & Compatibility Analyzer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "qnx_sentinel": [
            "templates/*",
            "templates/web/*",
        ]
    },
    entry_points={
        "console_scripts": [
            "qnx-sentinel=qnx_sentinel.cli:main",
        ],
    },
    python_requires=">=3.8",
)
