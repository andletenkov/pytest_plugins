import os
import pathlib
import shutil
import zipfile


def print_(text, *args, **kwargs):
    text_color = "\033[94m"
    end = '\033[0m'
    print(text_color + text + end, *args, **kwargs)


def compress_to_zip(folder, zip_name):
    files = [file for _, _, file in os.walk(folder)][0]
    with zipfile.ZipFile(zip_name, "w") as zipf:
        for file in files:
            zipf.write(
                filename=str(pathlib.PurePath(folder, file)),
                arcname=os.path.basename(file),
                compress_type=zipfile.ZIP_DEFLATED
            )


def cleanup(*items):
    for item in items:
        if os.path.isfile(item):
            os.remove(item)
        elif os.path.isdir(item):
            shutil.rmtree(item, ignore_errors=True)
