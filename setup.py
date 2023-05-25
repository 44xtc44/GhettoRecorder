import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

# ###############################################

pack_name = "ghettorecorder"
pack_version = "3.0.0"
pack_description = "Inet radio grabber"

INSTALL_REQUIRES = ['aacRepair', 'certifi', 'configparser']
PYTHON_REQUIRES = '>=3.7'

setuptools.setup(

    name=pack_name,  # project name /folder
    version=pack_version,
    author="René Horn",
    author_email="rene_horn@gmx.net",
    description=pack_description,
    long_description=long_description,
    license='MIT License',
    long_description_content_type="text/markdown",
    url="",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        # How mature is this project? Common values are
        # https://packaging.python.org/guides/distributing-packages-using-setuptools/
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    ],
    python_requires=PYTHON_REQUIRES,
)
