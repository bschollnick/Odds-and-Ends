"""
    Directory Caching system.
    
    Used to speed up 
"""
import os
import os.path
import re
from stat import ST_MODE, ST_INO, ST_DEV, ST_NLINK, ST_UID, ST_GID, \
                    ST_SIZE, ST_ATIME, ST_MTIME, ST_CTIME
                    
import time
from datetime import timedelta
#from dicttime import dicttime

import scandir

plugin_name = "dir_cache"

#####################################################
# Source: http://nedbatchelder.com/blog/200712/human_sorting.html
# Author: Ned Batchelder
def tryint(s):
    """
    Convert to Integer
    """
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)
#####################################################

#class PluginOne(IPlugin):
#
#    def print_name(self):
#        print plugin_name


class   CachedDirectory:
    """
    
        
    For example:
        

    """
    def __init__(self):
        self.files_to_ignore = ['.ds_store', '.htaccess']
        self.root_path = None 
            # This is the path in the OS that is being examined
            #    (e.g. /Volumes/Users/username/)
        self.directory_cache = {}
        

    def _scan_directory_list(self, scan_directory):
        """
            Scan the directory "scan_directory", and save it to the
            self.directory_cache dictionary.
            
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
        return
        
    def directory_in_cache(self, scan_directory):
        """
            Pass the target directory 
        
            Will return True if the directory is already cached
            Will return False if the directory is not already cached
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        return scan_directory in self.directory_cache.keys()

    def directory_changed(self, scan_directory):
        """
            Pass the target directory as scan_directory.
        
            Will return True if the directory has changed, 
            or does not exist in cache.
        
            Returns False, if the directory exists in cache, and
            has not changed since the last read.
        
            This relies on the directory's Modified Time actually
            being updated since the last update.
        """
        if self.directory_in_cache(scan_directory):
            scan_directory = os.path.realpath(scan_directory).lower().strip()
            st = os.stat(scan_directory)
            return st[ST_MTIME] > self.directory_cache[scan_directory]\
                    ["last_scanned_time"]
        else:
            return True
    
    def smart_read(self, scan_directory):
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        if self.directory_changed(scan_directory):
             self._scan_directory_list(scan_directory)
             
        
    def return_sortfiles(self, scan_directory, reverse=False):
        """
        Return sorted keys from the Directory cache for scan_directory
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        keys = self.directory_cache[scan_directory]["files"].keys()
        return sorted(keys, reverse=reverse)
            
    def return_sortdirs(self, scan_directory, reverse=False):
        """
        Return sorted keys from the Files cache for scan_directory
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        keys = self.directory_cache[scan_directory]["dirs"].keys()
        return sorted(keys, reverse=reverse)
        
    def return_dir_count(self, scan_directory):
        """
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        return self.directory_cache[scan_directory]["number_dirs"]

    def return_file_count(self, scan_directory):
        """
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        return self.directory_cache[scan_directory]["number_files"]

                