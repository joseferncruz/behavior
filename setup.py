from setuptools import setup, find_namespace_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

requirements = [
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "scipy",
    "pingouin",
    "statsmodels",
    "sklearn",
]

#if __name__ == "__main__":
setup(
    name='Behavior',
    version='0.0.1',
    description='Code to analyse behavior',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jose Cruz, PhD',
    author_email='jose.cruz@nyu.edu',
    url='https://github.com/joseferncruz/behavior',
    packages=find_namespace_packages(include=["behavior.*"],
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    python_requires='>=3.6',
    zip_safe=False,
)

########## More information
# https://python-packaging-user-guide.readthedocs.io/tutorials/packaging-projects/
