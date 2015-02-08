import directory_caching

cdl = directory_caching.Cache()
cdl.smart_read( "/Users/Benjamin" )
dirs = cdl.return_sort_name(scan_directory="/Users/Benjamin")[1]

print "-"*10
print "Movies +0, should return current directory (e.g. movies)"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", 
            offset=0)]
print "-"*10
print "(Movies +2) Should be my games"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", 
            offset=2)]
print "-"*10
print "(movies -5) Should return Google drive"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Movies", 
            offset=-5)]
print "-"*10
print "Decrement from beginning by 2, should bounce back to .anyconnect"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Applications", 
            offset=-442)]
print "-"*10
print "Increment from beginning by 2, should be Calibre Library"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Applications", 
            offset=+2)]
print "-"*10
print "Decrease from end by 2, should be SmithMicrodownloader"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Wallpaper", 
            offset=-2)]
print "-"*10
print "Try to increment beyond dir listings.  Should bounce back to wallpaper"
print dirs[cdl.return_current_directory_offset(\
            scan_directory = "/Users/Benjamin", 
            current_directory="Wallpaper", 
            offset=+2)]
