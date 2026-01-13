#!/usr/bin/env python

# Copyright 2026 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages, setup

setup(
    name="datahub-action-glossary-export",
    version="0.1.0",
    description="DataHub Action to export glossary terms and nodes to Snowflake",
    author="Brock Griffey",
    author_email="brock@acryl.io",
    url="https://github.com/datahub-project/datahub",
    license="Apache License 2.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "acryl-datahub-actions>=0.0.9",
        "acryl-datahub>=0.8.34",
        "snowflake-connector-python>=3.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "datahub_actions.action.plugins": [
            "action-glossary-export = action_glossary_export:GlossaryExportAction",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
