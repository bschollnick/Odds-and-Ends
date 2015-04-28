#!/usr/bin/env python
"""
:Module: sort_downloads
:Date: 20150-20
:Platforms: Mac (Tested under Mac OS X)
:Version: 1
:Authors:
    - Benjamin Schollnick
:Copyright (C) 2015, Benjamin Schollnick
:License - MIT,

:Description:
    This will take a starting folder (e.g. Downloads folder), and move any
    files found in the directory, to a different folder
    (e.g. Sorted_Downloads), and organize by file types (based off extensions).
    Any file type not identified by a file type will be placed into a folder
    that is dated in the mm-dd-yyyy format.

    This allows better organization, and groups together files downloaded
    (generally) in the same day.

    Under MOSX, I use launchd to run this script, any time my download folder
    is updated.

**Modules Used (Batteries Included)**:

   * os
   * sys
   * datetime
   * time
   * shutil
   * logging

**Required 3rd Party Modules**:

   * None

"""
import os
import sys
import datetime
import shutil
import logging

INBOUND_DIR = r'/Volumes/Support/Support/incoming_downloads'
SORTED_DIRECTORY = r'/Volumes/4TB_Drive/sorted_downloads'


def return_datestamp(include_time=None):
    """
    Return the formatted time date string
    """
    datestamp = datetime.datetime.now()
    if not include_time:
        datestamp = str(datestamp).split(" ")[0]
    else:
        datestamp = str(datestamp).replace(":", "-")
    return datestamp


LOOKUP_TABLE = {'.TORRENT'  : "Torrents",
                '.DOWNLOAD' : None,
                '.DMG'      : "Disk Images",
                '.ISO'      : "Disk Images",
                '.ZIP'      : "Zip Files",
                '.JAR'      : "Java",
                '.SWF'      : "Flash",
                'PDF'       : "PDF",
                '.PY'       : "Python",
                '.PYC'      : "Python",
                '.WEBLOC'   : "BookMarks",
                '.EPUB'     : "Ebooks",
                '.RAR'      : "RAR",
                '.7Z'       : "7Z",
                '.TXT'      : "Text",
                '.PAGES'    : "Pages",
                '.HTM'      : "HTML",
                '.HTML'     : "HTML",
                '.CSS'      : "StyleSheet",
                '.JS'       : "JavaScript",
                '.CSV'      : "CSV",
                '.MPG'      : "Movie",
                '.MPEG'     : "Movie",
                '.M4V'      : "Movie",
                '.MOV'      : "Movie",
                '.AVI'      : "Movie",
                '.MP4'      : "Movie",
                '.EXE'      : "Windows",
                '.MSI'      : "Windows",
                '.DOC'      : "MS Word",
                '.DOCX'     : "MS Word",
                '.XLS'      : "Excel",
                '.XLSX'     : "Excel",
                '.PKG'      : "Macintosh",
                '.APP'      : "Macintosh",
               }

def return_new_path(filename):
    """
    Args:
        filename - the Fully qualified filename

    Returns:
        The name of the folder to place the file in

    """
    if os.path.isfile(filename):
        extension = os.path.splitext(filename)[1]
        if LOOKUP_TABLE.has_key(extension.upper()):
            output = LOOKUP_TABLE[extension.upper()]
            if output == None:
                output = filename
    else:
        output = filename
    return output

def main():
    """
    Args:
        None

    Returns:
        None

    """
    logger = logging.getLogger("FVS")
    loghandler = logging.FileHandler(sys.argv[0] + ".log")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    loghandler.setFormatter(formatter)
    logger.addHandler(loghandler)
    logger.setLevel(logging.WARNING)

    #
    #   Get the contents of the inbound_directory
    #
    contents_of_inbound = os.listdir(INBOUND_DIR)

    for file_x in contents_of_inbound:
        complete_filename = os.path.join(INBOUND_DIR, file_x.strip())
        if os.path.isfile(complete_filename) and not file_x.startswith("."):
            #       print return_new_path ( complete_filename )
            new_path = SORTED_DIRECTORY + \
                r"/%s" % return_new_path(complete_filename)
            logger.info("Moving ... %s to %s", file_x, new_path)
            if not os.path.exists(new_path):
                logger.warning("Making sorted directory - %s", new_path)
                os.mkdir(new_path)

            if os.path.exists(os.path.join(new_path, file_x)):
                #
                #   File Already exists, rename it to prevent naming conflicts
                #
                dstamp = return_datestamp(include_time=True)
                logger.warning(
                    "%s already exists, renaming to %s-%s",\
                    file_x, file_x, dstamp)
                fname, extension = os.path.splitext(complete_filename)
                new_filename = "%s-%s%s" % (fname, dstamp, extension)
                os.rename(complete_filename, new_filename)
                shutil.move(os.path.join(INBOUND_DIR, new_filename), new_path)
            else:
                #   Move the file, as is.
                if new_path.strip().upper() <> SORTED_DIRECTORY.strip().upper():
                    shutil.move(complete_filename, new_path)

    if os.path.exists(INBOUND_DIR + os.sep + ".DS_Store"):
        os.remove(INBOUND_DIR + os.sep + ".DS_Store")


if __name__ == "__main__":
    main()#
