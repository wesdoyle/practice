import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="practice",
    version="0.0.1",
    author="Wes D",
    packages=setuptools.find_packages(),
    python_requires=">=3.12",
)
