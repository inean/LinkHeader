#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name="hal-json",
      version="0.1",
      description="Parse and encode links according to RFC 5988 or HAL specs",
      author="Michael Burrows, Carlos Martín",
      author_email="inean.es@gmail.com",
      url="https://inean@github.com/inean/LinkHeader.git",
      packages=find_packages(),
      license="BSD",
      keywords="RFC5988, HAL, json",
      zip_safe=True,
      long_description="""
      A simple module to allow developers to format
      or encode links according to RFC 5988 or trying to follow HAL
      specifications (http://stateless.co/hal_specification.html)
      """,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ]
  )
