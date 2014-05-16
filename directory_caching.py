"""
    Directory Caching system.
    
    Used to cache & speed up directory listing.  

Preqs - 

    Scandir - https://github.com/benhoyt/scandir

    scandir is a module which provides a generator version of 
    os.listdir() that also exposes the extra file information the
    operating system returns when you iterate a directory.
    
    Generally 2-3 (or more) times faster than the standard library.
    (It's quite noticeable!)
"""
import os
import os.path
from stat import ST_MODE, ST_INO, ST_DEV, ST_NLINK, ST_UID, ST_GID, \
                    ST_SIZE, ST_ATIME, ST_MTIME, ST_CTIME
                    
import time
import scandir

plugin_name = "dir_cache"

#####################################################
class   CachedDirectory(object):
    """
    For example:
    
        To be added shortly.        

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
        directories = {}
        files = {}
        self.directory_cache[scan_directory.strip().lower()] = {}
        self.directory_cache[scan_directory.strip().lower()]["number_dirs"] = 0
        self.directory_cache[scan_directory.strip().lower()]["number_files"] = 0
        for x in scandir.scandir(scan_directory):
            st = x.lstat()
            data = {}
            data["fq_filename"] = os.path.realpath(scan_directory).lower() + \
                    os.sep+x.name.strip().lower()
            data["parentdirectory"] = os.sep.join(\
                    os.path.split(scan_directory)[0:-1])
            data["st_mode"] = st[ST_MODE]
            data["st_inode"] = st[ST_INO]
            data["st_dev"] = st[ST_DEV]
            data["st_nlink"] = st[ST_NLINK]
            data["st_uid"] = st[ST_UID]
            data["st_gid"] = st[ST_GID]
            data["compressed"] = st[ST_SIZE]
            data["st_size"] = st[ST_SIZE]       #10
            data["st_atime"] = st[ST_ATIME]     #11
            data["raw_st_mtime"] = st[ST_MTIME] #12
            data["st_mtime"] = time.asctime(time.localtime(st[ST_MTIME]))
            data["st_ctime"] = st[ST_CTIME]
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
        """
        This is a wrapper around the Read and changed functions.
        
        The scan_directory is passed in, converted to a normalized form,
        and then checked to see if it exists in the cache.  
        
        If it doesn't exist (or is expired), then it is read.
        
        If it already exists *AND* has not expired, it is not
        updated.
        
        Net affect, this will ensure the directory is in cache, and
        update to date.
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        if self.directory_changed(scan_directory):
            self._scan_directory_list(scan_directory)
             
        
    def return_sort_name(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by name.
        
        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        files = self.directory_cache[scan_directory]["files"]
        dirs = self.directory_cache[scan_directory]["dirs"]
        sorted_files = sorted(files.items(), 
                              key=lambda t: t[1]["filename"],
                              reverse=reverse)
        sorted_dirs = sorted(dirs.items(), 
                             key=lambda t: t[1]["directoryname"],
                             reverse=reverse)
        return (sorted_files, sorted_dirs)

    def return_sort_lmod(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by Last Modified.
        
        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        files = self.directory_cache[scan_directory]["files"]
        dirs = self.directory_cache[scan_directory]["dirs"]
        sorted_files = sorted(files.items(), 
                              key=lambda t: t[1]["raw_st_mtime"],
                              reverse=reverse)
        sorted_dirs = sorted(dirs.items(), 
                             key=lambda t: t[1]["raw_st_mtime"],
                             reverse=reverse)
        return (sorted_files, sorted_dirs)

    def return_sort_ctime(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by Creation Time.
        
        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).lower().strip()
        files = self.directory_cache[scan_directory]["files"]
        dirs = self.directory_cache[scan_directory]["dirs"]
        sorted_files = sorted(files.items(), 
                              key=lambda t: t[1]["st_ctime"],
                              reverse=reverse)
        sorted_dirs = sorted(dirs.items(), 
                             key=lambda t: t[1]["st_ctime"],
                             reverse=reverse)
        return (sorted_files, sorted_dirs)
            
