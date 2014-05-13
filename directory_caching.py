#from yapsy.IPlugin import IPlugin

import os
import os.path
from stat import ST_MODE, ST_INO, ST_DEV, ST_NLINK, ST_UID, ST_GID, \
                    ST_SIZE, ST_ATIME, ST_MTIME, ST_CTIME
                    
import time
from datetime import timedelta
#from dicttime import dicttime

import scandir

plugin_name = "dir_cache"

def natural_sort(l): 
    """
        http://stackoverflow.com/questions/4836710/
                does-python-have-a-built-in-function-for-string-natural-sort
    """
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
    
def fix_doubleslash(fullpathname):
    """
    Remove the Double Slashing that seems to occur.
    """
    while fullpathname.find("//") != -1:
        fullpathname = fullpathname.replace("//", "/")
    return fullpathname


#class PluginOne(IPlugin):
#
#    def print_name(self):
#        print plugin_name


class   UnifiedDirectory:
    """
    An Attempt to unify directories, and archives into
    one single storage package.
        
    For example:
        
            gallery_listings = unified.Unified_Directory()
#               gallery_listings.populate_file_data_from_filesystem(
                filepathname = directory_path)
            print "files: ",gallery_listings.files,"/n/n"
            print "subdirectories: ",gallery_listings.subdirectories
            print "Display Gallery for ", gallery_listings.root_path

    """
    def __init__(self):
        self.files_to_ignore = ['.ds_store', '.htaccess']
        self.root_path = None 
            # This is the path in the OS that is being examined
            #    (e.g. /Volumes/Users/username/)
        self.directory_cache = {}
        

    def _scan_directory_list(self, scan_directory):
        """
            Scan's the directory .
            
            Low Level function, intended to be used by the populate function.
        """
        scan_directory = os.path.abspath(scan_directory)
        parent_dir = os.sep.join(os.path.split(scan_directory)[0:-1])
        directories = {}
        files = {}
        counter = 0
        self.directory_cache[scan_directory.strip().lower()] = {}
        self.directory_cache[scan_directory.strip().lower()]["number_dirs"] = 0
        self.directory_cache[scan_directory.strip().lower()]["number_files"] = 0
        for x in scandir.scandir(scan_directory):
            st = x.lstat()
            data = {}
            data["fq_filename"] = os.path.realpath(scan_directory).lower() + \
                    os.sep+x.name.strip().lower()
            data["parentdirectory"] = parent_dir
            data["st_mode"] = st[ST_MODE]
            data["st_inode"] = st[ST_INO]
            data["st_dev"] = st[ST_DEV]
            data["st_nlink"] = st[ST_NLINK]
            data["st_uid"] = st[ST_UID]
            data["st_gid"] = st[ST_GID]
            data["compressed"] = st[ST_SIZE]
            data["st_size"] = st[ST_SIZE]
            data["st_atime"] = st[ST_ATIME]
            data["raw_st_mtime"] = st[ST_MTIME]
            data["st_mtime"] = time.asctime(time.localtime(st[ST_MTIME]))
            data["st_ctime"] = st[ST_CTIME]
            data["raw_index"] = counter
            data["sort_index"] = counter
            if not x.name.strip().lower() in self.files_to_ignore:
                if x.is_dir():
                    self.directory_cache[scan_directory.strip().lower()]\
                        ["number_dirs"] += 1
                    data["archivefilename"] = ""
                    data["filename"] = ""
                    data["directoryname"] = x.name.strip().lower()
                    data["dot_extension"] = ".dir"
                    data["file_extension"] = "dir"
                    directories[x.name.lower().strip()] = True
                    self._scan_directory_list(data["fq_filename"])
                    data["number_files"] = self.directory_cache\
                        [data["fq_filename"]]["number_files"]
                    data["number_dirs"] = self.directory_cache\
                        [data["fq_filename"]]["number_dirs"]
                    directories[x.name.lower().strip()] = data
                    
                else:
                    self.directory_cache[scan_directory.strip().lower()]\
                        ["number_files"] += 1
                    data["archivefilename"] = ""
                    data["filename"] = x.name.strip().lower()
                    data["directoryname"] = scan_directory
                    data["dot_extension"] = os.path.splitext\
                        (x.name)[1].lower()
                    data["file_extension"] = os.path.splitext\
                        (x.name)[1][1:].lower()
                    files[x.name.lower().strip()] = data
                counter += 1
                
        self.directory_cache[scan_directory.strip().lower()]["files"] = files
        self.directory_cache[scan_directory.strip().lower()]\
                ["dirs"] = directories
        self.directory_cache[scan_directory.strip().lower()]\
                ["last_scanned_time"] = time.time()
        return(directories, files)
