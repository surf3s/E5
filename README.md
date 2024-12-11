# E5 (Beta Version)

E5 is a generalized data entry program intended for archaeologists but likely useful for others as well.  It works with a configuration file where the data entry fields are defined.  Importantly, E5 makes it simple to make entry in one field conditional on values previously entered for other fields.  The goal is to make data entry fast, efficient and error free.

E5 is a complete, from scratch re-write of E4.  It is backwards compatible with E4 configuration files, but it supports several new features (with more to come).  For one, it is now built on Python to be cross-platform compatible, and the source code is available at GitHub.  E5 will run on Windows, Mac OS, Linux and Android tablets and phones.  For this reason and others, E5 now uses an open database format.  All data are stored in human readable, ASCII formatted JSON files.  Data can also be exported to CSV files for easy import into any database, statistics or spreadsheet software.

#### What's New

- Cross-platform support for Windows, Mac OS, Linux and Android
- JSON data format (CSV export)
- Open source
- DateTime field for automated recording of when the record was entered
- Boolean field for easy True/False recording
- Notes field for easier text entry
- Automated back-ups

#### What's Coming

- Support for device cameras to link images with data records
- Support for device GPS to link locations to data records
- Support for related tables with one to many relationships

#### What is Missing

- Support for iPhones.  Unfortunately the technology used for this version of E5 cannot be easily ported to iPhones.
- Support for older, serial port (COM) calipers and scales.  If there is a demand for this, I can consider adding it. I am interested in finding solutions for connecting calipers to Android phones as well.

#### A Word about the Technology

E5 is written with Python 3.8.1 (but is compatible with 3.6 for now) using as few dependencies as possible for portability and maintainability.  The graphical user interface is built on Kivy 2.0.  Kivy is specifically designed for touch screens and cross-platform support; however, I made every effort to retain the efficiency of keyboard data entry for Windows and Mac OS.  The database is built on TinyDB, which is written in pure Python.  E3 (the DOS version) lasted a good 15 years (and still works actually).  E4 lasted 10-15 years as well.  My hope is that E5 will have at least this same use life, and I am cautiously optimistic that the switch to Python will give it a longer use life (though I expect that I will have to change the graphical user interface technology more frequently).

#### Data Security and Bugs

E5 is a complete re-write of E4 in a language that I am still learning.  It also tries to do some things I have never done before (like cross-platform compatibility).  At the same time, E5 is responsible for your scientific data.  I can assure you that I take this responsibility, like the collection of my own data, very seriously, and I am making every effort to have a bug free program.  If you encounter bugs, please report them by emailing me at mcpherron@eva.mpg.de.  To effectively replicate the problem and fix the bug, I will need your configuration file, a description of how to replicate the bug, and the name of the platform (Windows, Android etc.).  If you want to add features, again, please write me.  And if you are a programmer and want to contribute features, that's great.  Please use GitHub so that I can incorporate your improvements into the general release versions (and I would prefer it if you contact me beforehand about working on the project).

#### Installation

##### Windows

A Windows exe file can be found in the folder [Windows](https://github.com/surf3s/E5/tree/master/E5/Windows).  Download this file, place it in a folder where you want to start your data entry, and launch the program.

I have tested E5 on several Windows 10 machines, and it worked well (though in some instance some of the time it was slow to load and then this problem went away).  I doubt it works on Windows 7 and it almost certainly does not work on Windows XP.  If you have to use Windows XP (and you really, really shouldn't) or Windows 7 (and you really, really shouldn't) then I recommend using my previous software (E4 or Entrer Trois).

If you know Python, you can also install the source code and run the program directly that way.

##### Mac OS

These instructions are similar to what is required for Linux.  Several things can vary.  Sometimes you type python to run Python and sometimes it is python3.  Just try them both.  You need one that gives you a version of Python of 3 or greater.  The same is true for pip.  Sometimes you use pip and sometimes pip3.  Again, just try it.  I think I would start in each case with python3 and pip3 and go from there.  If pip or pip3 do not work, you can try python3 -m pip instead of pip3 in the lines below.

```
pip3 install --upgrade pip wheel setuptools
pip3 install e5 --user
python3 -m e5py
```

To upgrade E5, you should be able to do the following.  Sometimes this does not work for me, so check the version number once you upgrade.

```
pip install --upgrade e5
```

##### Android

Works but I am still working on getting the code uploaded to the Google Play store.

##### Linux

The following has been tested on clean installs of Ubuntu.  There may be some small differences in the code base from what it stored on GitHub and what is pulled from PyPi using pip, but I will try to maintain both equally.  As with the Mac OS instructions above, you may need to replace the initial pip command with pip3 or maybe with python -m pip.  And you may need to replace python with python3.

```
pip install --upgrade pip wheel setuptools
pip install e5
python -m e5py
```

I prefer to do installations in a virtual environment to avoid Python conflicts.  To this you can use the following.  Again, you may need to use python3 instead of python and pip3 instead of pip.  These instructions assume you are in your home directory.

```
mkdir e5
cd e5
python -m venv ./venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install e5
python -m e5py
```

When you leave the virtual environment (either shutting down your computer or with the command source venv/bin/deactivate), you will need to reactivate your virtual environment before starting E5.  So navigate to your e5 folder again and do the following.

```
source venv/bin/activate
python -m e5py
```

To upgrade E5, you should be able to do the following.  Sometimes this does not work for me, so check the version number once you upgrade.

```
pip install --upgrade e5
```

##### Bug Fixes 

Version 1.3.17 (important - please update version)
1.  Fixed a huge bug with selecting items with the mouse.
2.  Fixed some issues with screen size and placement
3.  Fixed some issues with clicking outside a window
4.  Fixed an issue with how menus are displayed
      (this may fix the bouncing that sometimes happens)
      (and definitely makes the menus refresh smoother)
5.  Fixed an issue with moving MacOS CFGs to Windows

Version 1.3.16
1.  Substantial structural changes to accomodate moving the program to Google Play store

Version 1.3.15 (October, 2023)
1.  A lot more fixes to button and font sizing throughout (though some issues remain)
2.  Warning on settings changes that restart is required.

Version 1.3.14 (October, 2023)
1.  Fixed button sizing issues to work better on a variety of computers
2.  In menus, button height now tied to font size for button text
3.  In menus, number of menu columns tied to longest menu item and font size

Version 1.3.13 (October, 2023)
1.  Fixed issue with UNIQUE fields
2.  Fixed another issue with the Enter key

Version 1.3.12 (October, 2023)
1.  Moved fixes done in EDM over to E5 (should resolve a Mac formatting issue as well)
2.  Resolved a ton of data entry issues mostly related to keyboard entry

Version 1.3.11
1.  Brought in all changes made to EDMpy interface
2.  Fixed issue with parsing conditions - matches starting with NOT did not work (e.g. NOTCH)
3.  Put classes into separate files

Version 1.3 (June, 2022)

I finally had a chance to work on this and EDM.  The main effort here was to upgrade the program to Kivy 2.0 so that it would once again easily work across platforms.  This is done in the new version.  Additionally, I fixed a number of buys/annoyances including:
1.  Delete key now works in addition to backspace
2.  When only one record was present, the datagrid did not work properly.  This is fixed.
3.  When deleting records, sometimes the last record didn't show as deleted in the datagrid.  This is fixed.


#### Configuration Files

The key element of E5 is the configuration file where the data entry fields are defined.  Configuration files (ending with a CFG file extension) may seem a bit complicated at first, and they must be written in a separate program (an ASCII text editor like NotePad or NotePad++ on Windows).  The effort of thinking through a configuration file, however, means thinking through the structure of your data before you start collecting it (unlike, for instance, if you use a spreadsheet), and this effort typically pays off later when you go to analyze the data.

Several example CFG files are included here in the CFGs folder, and here is a sample configuration file to illustrate some features:

```
[E5]
TABLE=lithics

[ID]
TYPE=TEXT
PROMPT=Enter the artifact ID
UNIQUE=True

[ARTIFACTTYPE]
TYPE=MENU
PROMPT=Select the artifact type
MENU=Tool,Flake,Core

[TOOLTYPE]
TYPE=MENU
PROMPT=Select the tool type
MENU=Scraper,Notch,Point,Other
CONDITION1=ArtifactType Tool

[PLATFORMTYPE]
TYPE=MENU
PROMPT=What is the platform
MENU=Plain,Cortical,Missing,Other
CONDITION1=ArtifactType Tool,Flake

[PLATFORMWIDTH]
TYPE=NUMERIC
PROMPT=Measure the platform width
CONDITION1=ArtifactType Tool,Flake
CONDITION2=PlatformType not Missing

[WEIGHT]
TYPE=NUMERIC
PROMPT=WEIGHT
```

The file is organized into blocks defined by the [].  Each file will have an [E5] block (usually at the start) that contains settings that apply to the whole configuration file.  In this example, there is one option (table=) which tells E5 what to call the database table.  If no table is specified, E5 uses '_default'.  Because it is not specified here, the database file itself (a JSON file) will have the same name as the configuration file.

Next is a series of data entry fields (again, each defined with []).  Here the first field is an artifact ID.  The 'type' option tells E5 what kind of data to accept.  Valid options include text, note, numeric, menus, boolean (True/False), and the date and time.  The *prompt* is specified with an option, and then the *unique* option tells E5 that each data record must have a unique value for this field.  Attempts to duplicate a value for this field will generate a warning, and if data entry continues it will edit (or overwrite) the previous record with this ID.

The *ArtifactType* field demonstrates the use of menus.  The actual menu items are specified in the *menu* option and are comma separated.  There is no limit to the number of menu items, and they are displayed in the order specified here (unless the *sorted* option is set to *True*).  The *ToolType* field that follows is also a menu, but it demonstrates the use of conditionals.  During data entry, the *ToolType* menu will only be displayed when *ArtifactType* is a tool, otherwise E5 will skip to the next field and insert an empty string ("") for the *ToolType* field.

Likewise *PlatformType* is conditioned on the *ArtifactType* being a tool or a flake.  The field that follows, *PlatformWidth*, has two conditionals which must both be true otherwise the field will be skipped and an empty value will be inserted into the database table.  Notice that the second condition illustrates the use of the not keyword on conditions.  When the *PlatformType* is a value other than missing, this condition is true.

Both the *PlatformWidth* field and the last field, *Weight*, are numeric fields meaning that only valid numbers are accepted as input.  All other entries will generate an error and data entry cannot continue.

#### Details on Configuration Files (still a draft)

##### [E5]

###### database =

Name of the JSON file where the data will be stored. If a database is not specified, E5 will use the name of the CFG file and will create the database in the same folder as the CFG.  If the path is invalid or does not contain a database file, E5 will look for it first in the same folder as the CFG.

###### table =

The name of the data table within the database.  If a table is not specified, E5 will use the name '_default'.

##### [fieldname]

###### type =

Valid values are *text*, *note*, *numeric*, *instrument*, *menu*, *boolean*, *datetime*, *camera* (experimental) and *gps* (not yet implemented).  *Text* provides a one line entry box and accepts any alphanumeric characters.  *Note* is like *text* accept that provides a multiline entry box.  *Numeric* constrains input to valid numbers and an Android the keyboard defaults to numeric.  *Instrument* is retained for backwards compatibility but is now equivalent to *numeric*.  *Menu* works with the menu option (below) to provide a menu list.  *Boolean* is a menu with only two options (*True* and *False*).  *Datetime* automatically inserts the current date and time.  *Camera* is in testing mode but is intended to allow photos to be linked to data records.  A *GPS* feature is planned to also attach coordinates to data records.  If missing, type defaults to *text*.

###### prompt =

The prompt associated with each field.  If missing a default will be provided.

###### menu =

A comma separated menu list.  Unless the sorted option is specified (below), the menu list is shown in the order provided.  Pressing the first letters of the menu items filters to the list to matching values.

###### sorted =

If *True*, the menu list is sorted alphabetically.

###### length =

The maximum length of an entry.  Only valid for *text* and *note* fields.  The default is no limit.

###### info =

A message to be displayed for this field.

###### info file =

The name of a text file containing help text to be displayed for this field.  Unless a full path name is given, files are assumed to be in the same folder as the CFG.  If a full path is given, but this path is not valid or does not contain the file, E5 will search for the file in the same folder as the CFG.

###### increment =

If *True*, the numeric value in this field will be incremented by one each new record.  The default is *False*.

###### required =

Valid values are *True* and *False*.  Default is *false*.

###### unique =

If *True*, all entries in this field must be unique within the data table.  Entering a repeat value will generate a warning but data entry can continue.  However, when the record is saved, it will replace the previous record with this unique value.  If multiple unique fields are specified, they are all taken together to form a unique value.  For example, if there is one field called Square and another field called ID, E5 will generate a warning only when the combination of Square and ID are repeated within the data table.  The default is *False*.

###### carry =

If *True*, the previously entered value is retained as the default for the next data record. The default is *False*.

###### condition1 = conditional_field [not] conditional_matches [or]

Conditionals are a powerful feature of E5.  They are evaluated for each field as they are encountered, and if the result is *false*, the field is skipped.  There can be up to five conditions (each numbered condition1, condition2, etc.).  The first value of the condition is the conditional field.  This should be the name of a field previously encountered in the CFG.  Next, optionally, a *not* can be specified.  Next come the conditional matches.  These should be a comma separated list of values that could have been entered for the conditional field.  When the conditional field matches one of these, the condition is *true* unless *not* was specified in which case it is *false*.  If there are multiple conditions (e.g. condition1, condition2) then all conditions must be *true* unless *or* is specified.  In evaluating conditions with mixed *or*s and *and*s, *or*s are evaluated first and then the *and*s.  So, for instance, "*true* and *false* or *true*" results in *true* because "*false* or *true*" is *true* and then "*true* and *true*" is *true* (programmers note that the Python eval() function is used to evaluate conditions).  To test for an empty entry, use "" or '' in the conditional matches (e.g. compflake, proxflake, '' will match either a compflake, a proxflake or no entered value for the conditional field).

###### menu file =

The name of a file containing a list of values for a menu field.  These values should be one to a line. Unless a full path name is given, files are assumed to be in the same folder as the CFG.  If a full path is given, but this path is not valid or does not contain the file, E5 will search for the file in the same folder as the CFG.

#### Credits

*E5* is by Shannon P. McPherron.  It is based on *E4* also written by Shannon McPherron in collaboration with Harold L. Dibble.  *E4* was based on *Entrer Trois* which had the help also of Simon Holdaway.  All of these programs were written in the context of my own personal research but also excavation and analyses conducted by the *OldStoneAge* team.  Thus over the years the program has greatly benefit from their feedback.

