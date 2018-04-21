from setuptools import setup, find_packages


description = "A package for dynamically generating and handling frontend"\
	      " templates from canonical_args argspec dictionaries."

setup(name="canonical_args_frontend",
      version="0.1",
      description=description,
      author="Shonte Amato-Grill",
      author_email="shonte.amatogrill@gmail.com",
      maintainer="Shonte Amato-Grill",
      maintainer_email="shonte.amatogrill@gmail.com",
      url="https://github.com/shonteag/canonical_args_frontend",
      packages=find_packages(exclude=["test", "tests"]),
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Intended Audience :: Developers"
      ],
      install_requires=[
          "canonical_args==0.4",
          "Jinja2==2.1"
      ]
)
