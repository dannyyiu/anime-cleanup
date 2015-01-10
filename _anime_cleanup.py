#!/usr/bin/env python

from os import walk, path, rename, makedirs, rmdir
import time
import pprint


class AnimeCleanup(object):
    """
    Anime renaming and archiving automation utility.
    Run in same path where currently following anime files are stored.
    
    Episodes will be stripped of meta info, archived in folders, leaving only
    the last modified episode.
    """

    def __init__(self):
        self.fileList = []; # list of list [orig name, new name]
        
        self.shows = [] # list of current shows
        self.latestEps = [] # list of latest episodes
        self.shows_folders = [] # enum tuple of existing folder names
    
    def get_names(self):
        """ Get all filenames, prepare for cleanup. """
        for (dpath, dnames, fnames) in walk("."):
            self.shows_folders = dnames # directory names
            for fname in fnames:
                if ".mkv" in fname or ".mp4" in fname:
                    self.fileList.append([fname, ""])
            break

    def get_names_raw(self):
        """ Return list of all filenames. """
        # used when there is no need to use global vars
        flist = []
        for (dpath, dnames, fnames) in walk("."):
            for fname in fnames:
                if ".mkv" in fname or ".mp4" in fname:
                    flist.append(fname)
            break
        return flist
        
    
    def rm_meta(self, deep=None):
        """ Remove headers etc. Deep param to remove all items in []"""
        print "Removing brackets..."
        for i,f in enumerate(self.fileList):
            if f[0][0] == "[":
                temp = f[0][f[0].find("]")+1:].replace(
                    "_"," ").lstrip() # header removed
                if deep:
                    # deep rm
                    ext = temp[temp.rfind("."):] # extension
                    self.fileList[i][1] = "%s%s" % \
                        (temp[:temp.find("[")].rstrip(),ext) # deep rm
                else:
                    # keep some meta
                    self.fileList[i][1] = temp
    
    def fix_case(self):
        """ 
        Rename all filenames with case equal to existing
        folders with the same name. Done initially.
        """    
        print "\nFixing filename case mismatch..."
        if not self.shows_folders:
            self.get_names()
            self.fileList = []
        dlower = [dname.lower() for dname in self.shows_folders]
        for fname in self.get_names_raw():
            name = fname[:fname.find("- ")].rstrip()
            if name.lower() in dlower and \
                name not in self.shows_folders:
                i = dlower.index(name.lower())
                print "Case mismatch found: ", fname
                new_fname = self.shows_folders[i] + \
                    fname[fname.find(name)+len(name):] 
                print "New filename: ", new_fname
                rename(fname, new_fname)

    def fix_episodes(self):
        """
        Remove 'v2' etc from episode number.
        """
        print "Stripping episode version..."
        for fname in self.get_names_raw():
            end = fname[fname.find("- "):]
            if "v" in end[:end.find(".")]:
                new_fname = fname[:fname.find("- ")] + \
                    end[:end.find("v")] + \
                    end[end.find("."):]
                rename(fname, new_fname)
                print "\"v\" fixed:", new_fname

    def rename_all(self):
        """ Rename all fnames. """
        for [old,new] in self.fileList:
            if new:
                rename(old,new)
            
    def get_shows(self):
        """ Get a list of show names. Assume names cleaned up. """
        for fname in self.get_names_raw():
            name = fname[:fname.find("- ")].rstrip()
            if name not in self.shows:
                self.shows.append(name)
        print "\nSHOWS FOLLOWING:"
        for show in self.shows:
            print show
        
    def get_latest_eps(self):
        """ Get a list of latest episodes, to prevent archiving. """
        # dependencies
        if not self.shows:
            self.get_shows()
        # find latest ep fname for each show, based on create time
        for show in self.shows:
            dateCreated = 0 # int val for ctime
            ep_fname = ""
            for fname in self.get_names_raw():
                if show in fname:
                    name = fname[:fname.find("- ")].rstrip()
                    newTime = path.getctime(fname)
                    [dateCreated, ep_fname] = \
                        [[dateCreated, ep_fname], [newTime, fname]]\
                        [newTime >= dateCreated]
            self.latestEps.append(ep_fname)
        print "\nLATEST EPISODES: "
        for ep in self.latestEps:
            print ep
        
    def archive(self):
        """ Archive all but latest episode. """    
        if not self.latestEps:
            self.get_latest_eps()
            
        for show in self.shows:
            
            # move all eps except newest to folder
            for fname in self.get_names_raw():
                if show in fname and fname not in self.latestEps:
                    # create folder for archive, if not already exist
                    if not path.exists(show):
                        makedirs(show)
                    # move file
                    rename(fname, "%s/%s" % (show,fname))
            try:
                # remove folder if empty
                rmdir(show)
            except:
                pass
                
            
        
    def main(self):
        #renaming
        self.get_names() # get relevant filenames
        self.fix_case()
        self.fix_episodes()
        self.rm_meta(deep=1) # remove meta
        self.rename_all() # commit renaming
        
        #archiving
        self.get_shows() # get all show names currently following
        self.get_latest_eps() #get fnames of latest eps
        self.archive() # put all non-latest eps into archive
        
        
if __name__ == "__main__":
    a = AnimeCleanup()
    a.main()