#!python
#Author-Chris Drake
#Description-Update-checker for Airfoil Tools.  Loads the current version number of the latest Airfoil Tools release, asynchronously (in the background) into a text file in the user home folder.  Later, when Airfoil Tools ip opened, this file is read to determine if update info should be shown to the user.
#Copyright-(C)2020 Chris Drake.  All rights reserved.

# Usage: check_update.py [current version eg 1.20200503] [ctrl suffix eg _aft] [program name eg Airfoil_Tools] [database version eg 1.20200503] [check-time-offset]
#
# Tested u1.20200505 OK 20200503 mac, windows, linux
#
# NOTE: This only checks a max of one time per day (invoked by 'Airfoil Tools.py' on startup) unless check-time-offset occurred (re-checks for more updates immediately after doing any update)

import json, re, sys, datetime, os
# from os import altsep

VERSION='u1.20200602' # Version of our updater
print("Update Checker "+VERSION+" for Airfoil Tools Add-in to Autodesk Fusion 360.")


try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

this_ver=1.20200500
db_ver=1.20200500
aft='_aft'
program_name='Airfoil_Tools'
latest_ver = {'error':'Web update check failed'}
recheck=0


# Santize input of our existing version info
if len(sys.argv)>1 and re.search('^[A-za-z0-9\-][A-za-z0-9_\.\-]*$',sys.argv[1]):   # alphanums only
    this_ver=sys.argv[1]        # 1.20200503 / 1.20200503db-4
if len(sys.argv)>2 and re.search('^[A-za-z0-9_\.\-]+$',sys.argv[2]):                # alphanums only, allowed to start with _
    aft=sys.argv[2]             # _aft               
if len(sys.argv)>3 and re.search('^[A-za-z0-9_\.\-]+$',sys.argv[3]):                # alphanums only, allowed to start with _ - already had " " replaced.
    program_name=sys.argv[3]    # Airfoil_Tools
if len(sys.argv)>4 and re.search('^[A-za-z0-9_\.\-]+$',sys.argv[4]):                # alphanums only, allowed to start with _
    db_ver=sys.argv[4]          # 1.20200528
if len(sys.argv)>5 and re.search('^[0-9]+$',sys.argv[5]):                           # time override
    recheck=int(sys.argv[5])    # 100000000                                         # gets subtracted from last_check_time to trigger a same-day re-check



# Find a cross-platform friendly and appropriate place to save user settings files (see also the main program which does this same thing)
def home_file(program_name,settings_filename):
    if sys.platform.startswith('linux'):
        home_folder='~/.local/share'                    # ~/.local/share/<AppName>
    elif sys.platform.startswith('darwin'):
        home_folder='~/Library/Application Support/'    # ~/Library/Application Support/<AppName>
    else:
        home_folder=os.path.join('~','AppData','Roaming')   # C:\Users\cnd\AppData\Roaming

    home_folder=os.path.expanduser(os.path.join(home_folder,program_name.replace(" ", "_")))
    os.makedirs(home_folder, exist_ok=True)
    return os.path.join(home_folder,settings_filename)

def load_user_settings(settings_file_only):                                     # Read user settings, like firstrun flag, units, history, helpers, etc
    settings_file=home_file(program_name,settings_file_only)                    # Put this in the correct user home folder
    try:
        with open(settings_file,'r', newline='\n', encoding='utf-8' ) as json_file:
            udata = json.load(json_file)
        udata['loaded']=True
    except:
        udata={"firstrun":True}
    return udata

def save_user_settings(settings_file_only):                                  # Save the settings that we want to remember between sessions etc.
    global userdata
    settings_file=home_file(program_name,settings_file_only)                    # Put this in the correct user home folder
    try:
        with open(settings_file,'w', newline='\n', encoding='utf-8') as json_file:
            userdata["unsaved"]=False
            json_file.write(json.dumps(userdata)+"\n")
            json_file.close()
    except:
        userdata["unsaved"]=True

def vlog(*args, **kwargs):                                                    # Print debug stuff to STDOUT
    print(*args, file=sys.stderr, **kwargs)


# Copied from main program - applies the update
# Get any updates that are awaiting - see also check_updates.py, the other half of this code.  Does not install updates (user gets asked first)
# Returns True if this is check_only and updates await.  Returns True if not check_only and all updates are applied
def updates(check_only):
    global updatedata
    latest_ver=updatedata
    uready=not check_only                                                       # starts with False for check_only, True for doing update (so doing-update returns "True" when done)
    ugotall=True
    nfiles=0

    #os.makedirs(home_folder, exist_ok=True)
    if latest_ver.get('updates',0):
        for updatefn in latest_ver['updates']:
            updfn=home_file(program_name, os.path.join('updates', updatefn))   # Put update files temporarily in the users data folder - the main program will apply the updates later if the user approves
            # check that the existing files, if any, are not corrupted, and remove if yes
            if os.path.isfile( updfn ):                     # Already fetched
                try:
                    if os.stat(updfn).st_size == latest_ver['updates'][updatefn]['len']:
                        uready=True
                        if check_only:
                            nfiles=nfiles+1
                            #vlog("{} Update file {} awaits".format(program_name,updfn))
                        else:
                            fn=os.path.join(prog_folder,updatefn)               # Work out where this needs to go
                            path=re.split("/|\\\\",fn)                          # Split path from filename, separator-agnostic
                            if path:
                                if len(path[0]) and path[0][-1]==':':
                                   path[0]=path[0]+os.sep                       # Python defaults to relative, but nothing else ever does...
                                fn=os.path.join(*path)                          # convert incoming / to outgoing \
                                path.pop()                                      # discard the file name 
                            vlog("{} Updating {} from {}".format(program_name,fn,updfn))
                            try:
                                if path: vlog('making path:{}.'.format(os.path.join(*path)))
                                if path: os.makedirs( os.path.join(*path), exist_ok=True)# Ensure path exists
                                with open( updfn, 'rb') as in_file:             # Open the temp file that was stored in the user home folder
                                    with open( fn, 'wb') as out_file:           # Prep to write to the target file
                                        out_file.write(in_file.read())          # Copy the file contents over
                                        out_file.close()
                                    in_file.close()
                                os.unlink(updfn)                                # Get rid of the updated file now
                            except:
                                vlog('{} Failed to update {} from {} - reason: {}'.format(program_name, fn, updfn, traceback.format_exc()))
                                ugotall=False                               # So caller knows we failed

                    else: # Wrong size - might still be downloading.  check_update.py takes care of removing corrupted files
                        uready=False
                        ugotall=False
                        vlog("{} Update file {} not fully downloaded yet".format(program_name,updfn))

                except: pass
            else: # not fetched, or, already done
                if check_only:
                    uready=False
                    ugotall=False
                    vlog("{} Update file {} not downloaded".format(program_name,updfn))

    if check_only and nfiles:
        vlog("{} of {} {} update file(s) await".format(nfiles,len(latest_ver['updates']),program_name))

    return uready and ugotall




update_file = 'latest_version'+aft+'.json'                                      # Created async by check_update.py - contains JSON from website with current version data in it
settings_file = 'user_settings'+aft+'.json'                                     # Things like firstrun flag, units, history helpers, etc - see also home_file() for where this gets put

userdata=load_user_settings(settings_file)                                      # Get the users settings, defaults, preferences, presets, etc - empty if doesn't exist
if userdata.get('applyupdate',0):                                               # Complete any file updates that might not have been applied earlier
    updates(False)                                                              # Does the update

update_file = home_file(program_name, update_file)                              # Put this in the correct user home folder

# Build our update-check URL, which tells the server which version (and of what) we now use, so it can customise return information about what's new.
upd_check_url='http://chrisdrake.com/Airfoil_Tools/check_update.asp?u='+VERSION+'&v=' + str(this_ver) + str(recheck) + '&db=' + str(db_ver) + '&a=' + aft + '&p=' + program_name 

# Get the latest version info from the internet
try:
    ver = urlopen(upd_check_url)
    latest_ver = json.loads(ver.read())
    print("Latest version: {}".format(latest_ver.get('current_version'+aft,'unknown')))
except:
    latest_ver = {'error':'web update check failed'}
    print('Check failed')

latest_ver['last_check_time']= int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()) - recheck


# Save the settings so the main program can check this later when the user opens one of our windows.
try:
    with open(update_file,'w', newline='\n', encoding='utf-8') as json_file:
        json_file.write(json.dumps(latest_ver)+"\n")
        json_file.close()
except:
    print('Problem writing latest version save file: ' + update_file)


# Get any updates that are awaiting - see "def updates" in "Airfoil Tools.py" for the companion side of this code
if latest_ver.get('updates',0):
    print('{} update file(s) found, downloading now...'.format(len(latest_ver['updates'])))
    for updatefn in latest_ver['updates']:
        updfn=home_file(program_name, os.path.join('updates', updatefn))   # Put update files temporarily in the users data folder - the main program will apply the updates later if the user approves

        # check that the existing files, if any, are not corrupted, and remove if yes
        if os.path.isfile( updfn ):                     # Already fetched
            print("Skipping already-downloaded: " + updfn)
            try:
                if os.stat(updfn).st_size != latest_ver['updates'][updatefn]['len']:     # Wrong size.  Future - also check shasum & sig
                    print("Removing corrupted previous-download: " + updfn)
                    os.unlink(updfn)
                print("OK")
            except: pass

        if not os.path.isfile( updfn ):                                         # Not already fetched (nb: not "else:" because might have been erased above)
            uurl = latest_ver['updates'][updatefn]['url']
            uurl = uurl.replace(" ", "%20")                                     # Python chokes on spaces
            path=re.split("/|\\\\",updfn)                                       # Split path from filename, separator-agnostic

            if path:
                if len(path[0]) and path[0][-1]==':':
                   path[0]=path[0]+os.sep                       # Python defaults to relative, but nothing else ever does...
                updfn=os.path.join(*path)                       # convert incoming / to outgoing \
                path.pop()                                      # discard the file name 

            if path: os.makedirs( os.path.join(*path), exist_ok=True)           # Ensure path exists
            upd = urlopen(uurl)                                                 # Prepare to read
            with open( updfn, 'wb') as upd_file:                                # Create our file in binary mode
                upd_file.write(upd.read())                                      # Write out everything we read until there's nothing left
                upd_file.close()                                                # all done
                print("Fetched " +updfn + " from " + latest_ver['updates'][updatefn]['url'])    # nobody sees the screen, but put info out there anyhow (good in debug mode when running from cmd line)
else:
    print("No updates suitable for your current version {}".format(this_ver))

# print(latest_ver)
# print(settings_file)


#if userdata.get('debug',0) and not sys.platform.startswith('darwin'):
#    value = input("Update complete. Hit enter to exit:-)\n")



'''

Notes:

[cnd@mac Airfoil Tools]$ python ./check_update.py 1.20200501 _aft Airfoil_Tools 1.20200529 1000000000 
Update Checker u1.20200529 for Airfoil Tools Add-in to Autodesk Fusion 360.
Latest version: 1.20200525
3 update file(s) found, downloading now...
Skipping already-downloaded: /Users/cnd/Library/Application Support/Airfoil_Tools/updates/foildb2020/foildb2020.py
OK
Fetched /Users/cnd/Library/Application Support/Airfoil_Tools/updates/Airfoil Tools.py from http://chrisdrake.com/Airfoil_Tools/check_update.asp/Airfoil Tools.py
Fetched /Users/cnd/Library/Application Support/Airfoil_Tools/updates/all_files.zip from http://chrisdrake.com/Airfoil_Tools/check_update.asp/all_files.zip
[cnd@mac Airfoil Tools]$


[cnd@mac Airfoil Tools]$ curl 'chrisdrake.com/Airfoil_Tools/check_update.asp?u=u1.20200529&v=1.20200501&db=1.20200529&a=_aft&p=Airfoil_Tools' | prettyj 
$s = {
       'updates' => {
                      'Airfoil Tools.py' => {
                                              'url' => 'http://chrisdrake.com/Airfoil_Tools/check_update.asp/Airfoil Tools.py',
                                              'len' => 180068,
                                              'sha256' => 'a52ecb301551785e4afa68558fba044119dc6f85'
                                            },
                      'foildb2020/foildb2020.py' => {
                                                      'sha256' => '3d903e9f501ff63a3a780bf89ddfffd6156a3842',
                                                      'len' => 1775499,
                                                      'url' => 'http://chrisdrake.com/Airfoil_Tools/check_update.asp/foildb2020.py'
                                                    },
                      'all_files.zip' => {
                                           'len' => 2237568,
                                           'url' => 'http://chrisdrake.com/Airfoil_Tools/check_update.asp/all_files.zip',
                                           'sha256' => 'd1977d5b23dfba5fcf4aeab38f3551'
                                         }
                    },
       'current_version_aft' => '1.20200525',
       'sig' => '8ef8a6357e8f621d37c4c067af97448f',
       'update_msg' => '<div><p><b>Update Available</b>: New airfoil database. New main program.</p>'
     };
[cnd@mac Airfoil Tools]$ cat  ~/Library/Application\ Support/Airfoil_Tools/latest_version_aft.json                                             
{"current_version_aft": 1.20200525, "updates": {"foildb2020/foildb2020.py": {"url": "http://chrisdrake.com/Airfoil_Tools/check_update.asp/foildb2020.py", "len": 1775499, "sha256": "3d903e9f501ff63a3a780bf89ddfffd6156a3842"}, "Airfoil Tools.py": {"url": "http://chrisdrake.com/Airfoil_Tools/check_update.asp/Airfoil Tools.py", "len": 180068, "sha256": "a52ecb301551785e4afa68558fba044119dc6f85"}, "all_files.zip": {"url": "http://chrisdrake.com/Airfoil_Tools/check_update.asp/all_files.zip", "len": 2237568, "sha256": "d1977d5b23dfba5fcf4aeab38f3551"}}, "sig": "8ef8a6357e8f621d37c4c067af97448f", "update_msg": "<div><p><b>Update Available</b>: New airfoil database. New main program.</p>", "last_check_time": 590839659}

[cnd@mac Airfoil Tools]$ dir ~/Library/Application\ Support/Airfoil_Tools/updates/                    
drwxr-xr-x  3 cnd  staff       96 29 May 02:02 foildb2020/
-rw-r--r--  1 cnd  staff      375 30 May 11:54 Airfoil Tools.py
-rw-r--r--  1 cnd  staff  2237568 30 May 11:54 all_files.zip



:set tabstop=4
:set softtabstop=4
:set shiftwidth=4
:set expandtab

'''
