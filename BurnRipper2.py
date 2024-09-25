"""
Burn manifest file ripper v2

Rips all externally packaged payloads from a Burn Manifest XML
"""

import xml.etree.ElementTree as et
import sys
import os
import urllib.request
import shutil
from pathlib import Path
import argparse

def load_xml(path):
	"""
	Load xml from a file
	"""
	
	return et.fromstring(Path(path).read_text())

def strip_xml_namespaces(element):
	"""
	Remove the namespace prefixes, makes the manifest easier to work with
	"""
	
	for e in element:
		strip_xml_namespaces(e)
	
	if (element.tag.startswith("{http://schemas.microsoft.com/wix/2008/Burn}")):
		element.tag = element.tag[44:]
	
	return element

def download_file(path, url):
	"""
	Save a file to disk, making dirs if needed
	"""
	
	os.makedirs(Path(path).parent, exist_ok = True)
	
	with urllib.request.urlopen(url) as r:
		with open(path, "wb") as f:
			shutil.copyfileobj(r, f)
	
	return path

def rip_files(output_dir, manifest_path):
	"""
	Rip the files in a Burn manifest
	"""
	
	os.makedirs(output_dir, exist_ok = True)
	
	burn_manifest = strip_xml_namespaces(load_xml(manifest_path))
	
	if (burn_manifest.tag != "BurnManifest"):
		print(f"Error: File is not a Burn manifest!")
		return
	
	for sub in burn_manifest:
		if (sub.tag == "Payload"):
			id = sub.attrib["Id"]
			path = f"{output_dir}/" + sub.attrib["FilePath"].replace("\\", "/")
			hash = sub.attrib["Hash"]
			
			if ("DownloadUrl" in sub.attrib):
				url = sub.attrib["DownloadUrl"]
				print(f"Downloading {id} to {path}...")
				download_file(path, sub.attrib["DownloadUrl"])
			else:
				print(f"Skipping payload {id} (Packaging={sub.attrib['Packaging']})")

def main():
	args = argparse.ArgumentParser(prog="BurnRipper2", description="Rips externally packaged payloads from Burn manifests")
	args.add_argument("output", help="Output directory")
	args.add_argument("manifest", help="Manifest file")
	args = args.parse_args()
	
	rip_files(args.output, args.manifest)

if __name__ == "__main__":
	main()
