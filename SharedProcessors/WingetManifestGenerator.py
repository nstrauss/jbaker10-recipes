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
import pathlib
import plistlib

from Foundation import NSArray, NSDictionary, NSUserName, NSHomeDirectory
from collections import defaultdict

from os.path import expanduser
from CoreFoundation import CFPreferencesCopyAppValue
from autopkglib import Processor, ProcessorError

__all__ = ["WingetManifestGenerator"]


class IndentDumper(yaml.Dumper):
    """Helper class to ensure the YAML file is indented properly"""

    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


class WingetManifestGenerator(Processor):
    """Creates a winget yaml manifest for new versions of apps"""

    description = __doc__

    input_variables = {
        "application_name": {
            "description": "The name of the installer",
            "required": True,
        },
        "manifest_output_path": {
            "description": "Output directory of the generated winget manifest",
            "required": True,
        },
        "manifest_output_filename": {
            "description": "Filename of the winget manifest",
            "required": True,
        },
        "package_id": {
            "description": "The package Id in the format <Publisher.Appname>",
            "required": True,
        },
        "publisher": {"description": "Publisher of the app", "required": True},
        "version": {"description": "The version of the app", "required": True},
        "installer_type": {
            "description": "The Installer type. Supported types are inno, wix, msi, nullsoft, zip, appx, msix and exe.",
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

    output_variables = {
        "manifest_dump": {"description": "JSON dump of the winget manifest generated"}
    }

    def generate_sha256_of_file(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def generate_sha256_of_bytes(self, data):
        return hashlib.sha256(
            yaml.dump(data, sort_keys=False, Dumper=IndentDumper).encode("utf-8")
        ).hexdigest()

    def check_path_exists(self, path, type="file"):
        if type == "directory":
            if os.path.isdir(path):
                return True
            else:
                return False
        else:
            if os.path.isfile(path):
                return True
            else:
                return False

    def make_directory(self, path):
        try:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.output(
                f"An exception occurred while trying to create the manifest_output_path [{path}]: {e}"
            )

    def main(self):
        self.output("Using WingetYamlGenerator version: 0.1.0")
        manifest_template = {}
        manifest_template["Id"] = self.env.get("package_id", "")
        manifest_template["Version"] = self.env.get("version", "")
        manifest_template["Name"] = self.env.get("application_name", "")
        manifest_template["Publisher"] = self.env.get("publisher", "")
        manifest_template["License"] = self.env.get("license_type", "")
        if self.env.get("license_url", ""):
            manifest_template["LicenseUrl"] = self.env.get("license_url", "")
        if self.env.get("app_moniker", ""):
            manifest_template["AppMoniker"] = self.env.get("app_moniker", "")
        if self.env.get("tags", ""):
            manifest_template["Tags"] = self.env.get("tags", "")
        manifest_template["InstallerType"] = self.env.get("installer_type", "")
        manifest_template["Installers"] = []
        for installer in self.env.get("installers", []):
            installer_metadata = {
                "Arch": installer.get("architecture", ""),
                "Url": installer.get("download_url", ""),
                "Sha256": self.generate_sha256_of_file(
                    self.env.get("destination_path", "")
                ),
            }
            if installer.get("language", ""):
                installer_metadata["Language"] = self.env.get("language", "")
            if installer.get("switches", {}):
                installer_metadata["Switches"] = installer.get("switches", {})
            if installer.get("scope", ""):
                installer_metadata["Scope"] = installer.get("scope", "")

            manifest_template["Installers"].append(installer_metadata)
        # ensure manifest output path exists before dumping YAML
        self.make_directory(path=self.env.get("manifest_output_path", ""))
        full_output_path = os.path.join(
            self.env.get("manifest_output_path", ""),
            self.env.get("manifest_output_filename", ""),
        )
        # check if manifest with same name already exists
        self.output(
            f"Checking if manifest {self.env.get('manifest_output_filename', '')} for {self.env.get('application_name', '')} already exists"
        )
        if self.check_path_exists(path=full_output_path):
            self.output(
                f"A manifest for {self.env.get('manifest_output_filename', '')} already exists on disk, checking if contents have changed since last run"
            )
            existing_manifest_hash = self.generate_sha256_of_file(path=full_output_path)
            new_manifest_hash = self.generate_sha256_of_bytes(data=manifest_template)
            if new_manifest_hash == existing_manifest_hash:
                self.output(
                    "Manifest on disk has not changed, making no further updates"
                )
            else:
                self.output(
                    f"Manifest has changed, updating contents of {self.env.get('manifest_output_filename', '')}"
                )
                # write new manifest file to disk
                with open(full_output_path, "w") as f:
                    yaml.dump(
                        manifest_template, f, sort_keys=False, Dumper=IndentDumper
                    )
        else:
            self.output(
                f"Manifest {self.env.get('manifest_output_filename', '')} does not yet exist, creating manifest now"
            )
            # write new manifest file to disk
            with open(full_output_path, "w") as f:
                yaml.dump(manifest_template, f, sort_keys=False, Dumper=IndentDumper)

        self.env["manifest_dump"] = json.dumps(manifest_template, indent=4)


if __name__ == "__main__":
    processor = WingetManifestGenerator()
    processor.execute_shell()
