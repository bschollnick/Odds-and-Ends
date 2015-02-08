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

    natsort - Used for natural sorting when returning alpha results
"""
#   Batteries Included imports
import os
import os.path
import stat
import string
import time

#   Required third party
import natsort  # https://github.com/xolox/python-naturalsort
import scandir  # https://github.com/benhoyt/scandir

#####################################################

class Cache(object):
    """
    For example:

        To be added shortly.        

    """
    def __init__(self):
        self.files_to_ignore = ['.ds_store', '.htaccess']
        self.root_path = None
        # This is the path in the OS that is being examined
        #    (e.g. /Volumes/Users/username/)
        self.d_cache = {}

    class entry(object):
        """
            Used to store data regarding the files or subdirectories.

            number_files, and number_dirs are only used by 
            directories.  It contains the number of files, or
            subdirectories in the directory.

            directoryname coresponds to the directoryname
            the file is in.

            parentdirectory is the name of the parent directory
            of the file or directory.

            file_extension is the extension in "xxx" format
            dot_file_extension is the extension in ".xxx" format

            filename is the filename of the file

            fq_filename is the fully qualified filename

            st stores the statistics for the file/directory

                st_mode - Filemode
                st_ino
                st_dev
                st_nlink
                st_uid
                st_gid
                st_size
                st_atime
                st_mtime
                st_ctime

            human_st_mtime contains the human readable modified time.        

        """

        def __init__(self):
            self.number_files = None
            self.number_dirs = None
            self.parentdirectory = None
            self.directoryname = None
            self.file_extension = None
            self.dot_extension = None
            self.filename = None
            self.fq_filename = None
            self.st = None
            self.human_st_mtime = None
            self.directory = None

    def _scan_directory_list(self, scan_directory):
        """
            Scan the directory "scan_directory", and save it to the
            self.d_cache dictionary.

            Low Level function, intended to be used by the populate function.

            scan_directory is matched absolutely, case sensitive, 
            string is stripped(), but otherwise left alone.

            Highly recommend using a normalization routine on the
            scan_directory string before sending it to cache.
        """
        scan_directory = os.path.abspath(scan_directory)
        directories = {}
        files = {}
        norm_dir_name = scan_directory.strip()
        self.d_cache[norm_dir_name] = {}
        for x in scandir.scandir(scan_directory):
            data = self.entry()
            data.st = x.lstat()
            data.fq_filename = os.path.join(
                os.path.realpath(scan_directory.strip()),
                x.name.strip())
            data.parentdirectory = os.path.join(
                os.path.split(scan_directory)[0:-1])
            data.human_st_mtime = time.asctime(
                time.localtime(data.st[stat.ST_MTIME]))
            if x.name.strip().lower() in self.files_to_ignore:
                continue
            if x.is_dir():
                data.filename = ""
                data.directoryname = x.name.strip()
                data.dot_extension = ".dir"
                data.file_extension = "dir"
                directories[x.name.strip()] = True
                # self._scan_directory_list(data.fq_filename)
#                temp = scandir.scandir(data.fq_filename)
                directories[x.name.strip()] = data
            else:
                data.filename = x.name.strip()
                data.directoryname = scan_directory
                data.dot_extension = string.lower(os.path.splitext(x.name)[1])
                data.file_extension = data.dot_extension[1:]
                files[x.name.strip()] = data
        self.d_cache[norm_dir_name]["files"] = files
        self.d_cache[norm_dir_name]["dirs"] = directories
        self.d_cache[norm_dir_name]["last_scanned_time"] = time.time()
        return

    def directory_in_cache(self, scan_directory):
        """
            Pass the target directory 

            Will return True if the directory is already cached
            Will return False if the directory is not already cached
        """
        scan_directory = os.path.realpath(scan_directory).strip()
        return scan_directory in self.d_cache.keys()

    def return_current_directory_offset(self, 
                                        scan_directory, 
                                        current_directory, 
                                        offset=0,
                                        sort_type=0):
        """
    return the offset of the next or previous directory, in scan_directory,
    where current_directory is the current_directory that you are residing in 
    from the scan_directory.
    
    e.g. /Users/Benjamin is the scan_directory, you are in Movies.  So 
    current_directory is Movies.  
    
    Used for calculating the previous / next directory in the gallery.

        offset  = 0, return current directories offset
                = -1, return the previous directory
                = +1, return the next directory in the list
    
    Example:
    
    cdl = d_caching.Cache()
    cdl.smart_read( "/Users/Benjamin" )
    dirs = cdl.return_sort_name(scan_directory="/Users/Benjamin")[1]
    print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", offset=0)]

    print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", offset=2)]
    print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", offset=-2)]
        """
        scan_directory = os.path.realpath(scan_directory).strip()
        if sort_type in [0, 1]:
            #   Named Sort - 0, reverse name sort - 1
            dirs = self.return_sort_name(scan_directory=scan_directory,
                                        reverse=sort_type in [1])[1]
        elif sort_type in [2, 3]:
            dirs = self.return_sort_lmod(scan_directory=scan_directory,
                                        reverse=sort_type in [0])[1]
        elif sort_type in [4, 5]:
            dirs = self.return_sort_ctime(scan_directory=scan_directory,
                                        reverse=sort_type in [1])[1]
        current_offset = None
        for x in range(0, len(dirs)):
            if dirs[x][0].lower().strip() == current_directory.lower().strip():
                current_offset = x
                break
        if offset == 0:
            return current_offset
        
        if current_offset == None:
            #
            #   Empty Directory?  Was not found in the for loop.
            #
            return None

        if offset < 0:
            #
            #   Negative Offset
            #
            if current_offset + offset >= 0:
                # offset is negative X
                return current_offset + offset
            else:
                return 0
        else:
            if current_offset + offset > len(dirs):
                return len(dirs)-1
            else:
                return current_offset + offset
        
        
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
#        print "Directory - ", scan_directory
#        print "exists : ",self.directory_in_cache(scan_directory)
        if self.directory_in_cache(scan_directory):
            scan_directory = os.path.realpath(scan_directory).strip()
            st = os.stat(scan_directory)
            return st[stat.ST_MTIME] > self.d_cache[scan_directory]\
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
#        print "Scan directory - ", scan_directory
#        print "real path ",os.path.realpath(scan_directory)
        scan_directory = os.path.realpath(scan_directory).strip()
#        print "Changed - ",self.directory_changed(scan_directory)
        if self.directory_changed(scan_directory):
            self._scan_directory_list(scan_directory)

    def return_sort_name(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by name.

        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).strip()
        files = self.d_cache[scan_directory]["files"]
        dirs = self.d_cache[scan_directory]["dirs"]
        sorted_files = natsort.natsort(files.items(),
                               key=lambda t: string.lower(t[1].filename),
                               reverse=reverse)
        sorted_dirs = natsort.natsort(dirs.items(),
                              key=lambda t: string.lower(t[1].directoryname),
                              reverse=reverse)
        return (sorted_files, sorted_dirs)

    def return_sort_lmod(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by Last Modified.

        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).strip()
        files = self.d_cache[scan_directory]["files"]
        dirs = self.d_cache[scan_directory]["dirs"]
        sorted_files = sorted(files.items(),
                              key=lambda t: t[1].st.st_mtime,
                              reverse=reverse)
        sorted_dirs = sorted(dirs.items(),
                             key=lambda t: t[1].st.st_mtime,
                             reverse=reverse)
        return (sorted_files, sorted_dirs)

    def return_sort_ctime(self, scan_directory, reverse=False):
        """
        Return sorted list(s) from the Directory Cache for the
        Scanned directory, sorted by Creation Time.

        Returns 2 tuples of date, T[0] - Files, and T[1] - Directories
        which contain the data from the cached directory.
        """
        scan_directory = os.path.realpath(scan_directory).strip()
        files = self.d_cache[scan_directory]["files"]
        dirs = self.d_cache[scan_directory]["dirs"]
        sorted_files = sorted(files.items(),
                              key=lambda t: t[1].st.st_ctime,
                              reverse=reverse)
        sorted_dirs = sorted(dirs.items(),
                             key=lambda t: t[1].st.st_ctime,
                             reverse=reverse)
        return (sorted_files, sorted_dirs)
