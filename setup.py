import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="balticlsc",
    version="0.0.5",
    author="Jan Bielecki",
    author_email="jan.bielecki.dokt@pw.edu.pl",
    description="Baltic LSC python balticlsc scheme",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/K4liber/balticlsc_module",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
