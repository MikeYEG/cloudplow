import hashlib
import os
from pathlib import Path

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote

import logging

log = logging.getLogger('path')


def get_file_extension(file):
    extensions = Path(file).suffixes
    extension = ''.join(extensions).lstrip('.')
    return extension.lower()


def get_file_hash(file):
    # get file size for hash
    file_size = 0
    try:
        file_size = os.path.getsize(file)
    except:
        log.exception("Exception getting file size of %r: ", file)
    # set basic string to use for hash
    key = "{filename}-{size}".format(filename=os.path.basename(file), size=file_size)
    return hashlib.md5(key.encode('utf-8')).hexdigest()


def find_files(folder, extension=None, depth=None):
    file_list = []
    start_count = folder.count(os.sep)
    for path, subdirs, files in os.walk(folder, topdown=True):
        for name in files:
            if depth and path.count(os.sep) - start_count >= depth:
                del subdirs[:]
                continue
            file = os.path.join(path, name)
            if not extension:
                file_list.append(file)
            else:
                # file_extension = get_file_extension(file)
                if file.lower().endswith(extension.lower()):
                    file_list.append(file)

    return file_list


def find_folders(folder, extension=None, depth=None):
    folder_list = []
    start_count = folder.count(os.sep)
    for path, subdirs, files in os.walk(folder, topdown=True):
        for name in subdirs:
            if depth and path.count(os.sep) - start_count >= depth:
                del subdirs[:]
                continue
            file = os.path.join(path, name)
            if not extension:
                folder_list.append(file)
            elif file.lower().endswith(extension.lower()):
                folder_list.append(file)
    return folder_list


def opened_files(path):
    files = []

    try:
        process = os.popen('lsof -wFn +D %s | tail -n +2 | cut -c2-' % cmd_quote(path))
        data = process.read()
        for item in data.split('\n'):
            if not item or len(item) <= 3 or os.path.isdir(item) or item.isdigit():
                continue
            files.append(item)

        return files

    except:
        log.exception("Exception retrieving open files from %r: ", path)
    return []


def delete(path):
    if isinstance(path, list):
        for item in path:
            if os.path.exists(item):
                log.debug("Removing %r", item)
                try:
                    if not os.path.isdir(item):
                        os.remove(item)
                    else:
                        os.rmdir(item)
                except:
                    log.exception("Exception deleting '%s': ", item)
            else:
                log.debug("Skipping deletion of '%s' as it does not exist", item)
    else:
        if os.path.exists(path):
            log.debug("Removing %r", path)
            try:
                if not os.path.isdir(path):
                    os.remove(path)
                else:
                    os.rmdir(path)
            except:
                log.exception("Exception deleting '%s': ", path)
        else:
            log.debug("Skipping deletion of '%s' as it does not exist", path)