from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="wagtail-gatsby",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    description="Plugin to enable support for gatsby-source-wagtail.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathhorrigan/wagtail-gatsby",
    author="Nathan Horrigan",
    author_email="Nathan.Horrigan@torchbox.com",
    license="BSD",
    install_requires=["wagtail>=2.0"],
    extras_require={},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)