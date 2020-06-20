#!/usr/local/autopkg/python
#
# Copyright 2020 Jeremiah Baker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import yaml
import time
import hashlib
import plistlib

from Foundation import NSArray, NSDictionary, NSUserName, NSHomeDirectory

from os.path import expanduser
from CoreFoundation import CFPreferencesCopyAppValue
from autopkglib import Processor, ProcessorError

__all__ = ["WingetYamlGenerator"]


class WingetYamlGenerator(Processor):
    """Creates a winget yaml manifest for new versions of apps"""

    description = __doc__

    input_variables = {
        "application_name": {
            "description": "The name of the installer",
            "required": True,
        },
        "manifest_path": {
            "description": "Output path of the generated winget manifest",
            "required": True,
        },
        "package_id": {
            "description": "The package Id in the format <Publisher.Appname>",
            "required": True,
        },
        "publisher": {"description": "Publisher of the app", "required": True},
        "version": {"description": "The version of the app", "required": True},
        "installer_type": {
            "description": "The Installer type, i.e. exe, msi, msix, inno, nullsoft",
            "required": True,
        },
        "installers": {
            "description": "List of installers and install instructions for the package",
            "required": True,
            "subkeys": {
                "download_url": {
                    "description": "The Url to download the installer",
                    "required": True,
                },
                "architecture": {
                    "description": "The architecture supported by the installer (one of: x86, x64, arm, arm64, Neutral)",
                    "required": True,
                },
                "install_switches": {
                    "description": "A set of install command line switches that should be used",
                    "required": False,
                },
            },
        },
        "license_type": {
            "description": "Enter the software's license model, i.e. MIT, Copyright",
            "required": True,
        },
        "license_url": {
            "description": "Url of the software's licensing agreement",
            "required": False,
        },
        "app_moniker": {
            "description": "The friendly name of the app, i.e. vscode or 1password",
            "required": False,
        },
        "tags": {
            "description": "List of tags to be added to the manifest",
            "required": False,
        },
        "app_homepage_url": {
            "description": "The Url to the homepace of the application",
            "required": False,
        },
        "description": {
            "description": "A description of the application",
            "required": False,
        },
    }

    manifest_template = {
        "Id": "",
        "Version": "",
        "Name": "",
        "Publisher": "",
        "License": "",
        "Installers": [],
    }

    def generate_sha256(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def main(self):
        self.output("[+] Using WingetYamlGenerator version: 0.1.0")
        manifest_template["Id"] = self.env.get("package_id", "")
        manifest_template["Version"] = self.env.get("version", "")
        manifest_template["Name"] = self.env.get("application_name", "")
        manifest_template["Publisher"] = self.env.get("publisher", "")
        manifest_template["License"] = self.env.get("license_type", "")
        for installer in self.env.get("installers", []):
            manifest_template["Installers"].append(installer)
        self.output(manifest_template)


if __name__ == "__main__":
    processor = WingetYamlGenerator()
    processor.execute_shell()
