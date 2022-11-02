import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    coverage_string: str = "![Coverage report](https://github.com/ZPascal/hana-injector/blob/main/docs/coverage.svg)"
    long_description: str = fh.read()

long_description = long_description.replace(coverage_string, "")

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
    #TODO Update the requirements
    install_requires=[],
    python_requires=">=3.6",
)
