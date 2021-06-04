#!/usr/bin/env python

import os
import sys
from zipfile import ZipFile


def clean_string(string: str) -> str:
    """Strips whitespaces and converts a string to snakecase.

    Args:
        string (str): target string

    Returns:
        str: clean string
    """
    return string.strip().lower().replace("  ", " ").replace(" ", "_")


def make_tempdir(file: str, base_path=None) -> str:
    """From a file and a base path, creates a new path for a temporary directory containing the file's name.
    """
    if base_path is None:
        base_path = os.getcwd()

    basename, _ = os.path.splitext(clean_string(file))

    return os.path.join(base_path, f"{basename}_temp")


def unzip_file(zip_file: str, workdir=None, destdir=None, temp_dir=False) -> None:
    """Extracts a zipfile, even to a dedicated temporary directory.

    Args:
        zip_file (str): the target zipfile.
        workdir (str, optional): The directory where the file is located. Defaults to the current working directory.
        destdir (str, optional): The directory where it will be extracted. Defaults to the current working directory.
        temp_dir (bool, optional): Triggers the extraction to a temporary directory. Defaults to False.
    """
    if workdir is None:
        workdir = os.getcwd()

    if destdir is None:
        destdir = workdir

    if temp_dir is True:
        destdir = make_tempdir(file=zip_file, base_path=destdir)

    with ZipFile(os.path.join(workdir, zip_file), "r") as zip:
        zip.extractall(destdir)
        print(f"{len(zip.namelist())} files have been extracted to {destdir}.")


def rename_dir_files(target_dir: str) -> None:
    """Cleans the names of all files in a target directory

    Args:
        target_dir (str): the directory where files need to be cleaned
    """
    for file in os.listdir(target_dir):
        os.rename(
            os.path.join(target_dir, file),
            os.path.join(target_dir, clean_string(file)),
        )


if __name__ == "__main__":

    zips = sys.argv[1:]

    for zip_file in zips:
        try:
            # name the temporary dir where to store the files
            extraction_dir = make_tempdir(zip_file)
            print(extraction_dir)

            # unzip the archive
            unzip_file(zip_file=zip_file, destdir=extraction_dir)

            # clean the names of the files extracted
            print("Cleaning the extracted file names...")
            rename_dir_files(extraction_dir)
            print("Filenames have been cleaned!")
        except:
            print(f"Invalid file: {zip_file}")
