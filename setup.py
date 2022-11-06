import setuptools
import os
from pathlib import Path
from typing import List

with open("README.md", "r", encoding="utf-8") as fh:
    coverage_string: str = "![Coverage report](https://github.com/ZPascal/hana-injector/blob/main/docs/coverage.svg)"
    long_description: str = fh.read()

long_description = long_description.replace(coverage_string, "")

with open(os.path.join(Path(__file__).parent, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs: List[str] = f.read().split('\n')

setuptools.setup(
    name="hana-injector",
    version="0.0.1",
    author="Pascal Zimmermann",
    author_email="info@theiotstudio.com",
    description="An MQTT stream to SAP HANA database injector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZPascal/hana-injector",
    project_urls={
        "Source": "https://github.com/ZPascal/hana-injector",
        "Bug Tracker": "https://github.com/ZPascal/hana-injector/issues",
        "Documentation": "https://zpascal.github.io/hana-injector/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    packages=["injector"],
    entry_points="""
        [console_scripts]
        hana-injector=injector.app:main
    """,
    install_requires=all_reqs,
    python_requires=">=3.6",
)
