# E5 (Alpha Version)

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

- Support for iPhones.  Unfortunately the technology used for this version of E5 cannot be easily ported to iPhones.  However, once this version is stable, I will begin work on a custom re-write for Android and Apple phones.
- Support for older, serial port (COM) calipers and scales.  If there is a demand for this, I can consider adding it. I am interested in finding solutions for connecting calipers to Android phones as well.

#### A Word about the Technology

E5 is written with Python 3.6.5 using as few dependencies as possible for portability and maintainability.  The graphical user interface is built on Kivy 1.11.0.  Kivy is specifically designed for touch screens and cross-platform support; however, I made every effort to retain the efficiency of keyboard data entry for Windows and Mac OS.  The database is built on TinyDB, which is written in pure Python.  E3 (the DOS version) lasted a good 15 years (and still works actually).  E4 lasted 10-15 years as well.  My hope is that E5 will have at least this same use life, and I am cautiously optimistic that the switch to Python will give it a longer use life (though I expect that I will have to change the graphical user interface technology more frequently).  

#### Data Security and Bugs

E5 is a complete re-write of E4 in a language that I am still learning.  It also tries to do some things I have never done before (like cross-platform compatibility).  At the same time, E5 is responsible for your scientific data.  I can assure you that I take this responsibility, like the collection of my own data, very seriously, and I am making every effort to have a bug free program.  If you encounter bugs, please report them by emailing me at mcpherron@eva.mpg.de.  To effectively replicate the problem and fix the bug, I will need your configuration file, a description of how to replicate the bug, and the name of the platform (Windows, Android etc.).  If you want to add features, again, please write me.  And if you are a programmer and want to contribute features, please use GitHub so that I can incorporate your improvements into the general release versions.

#### Configuration Files

The key element of E5 is the configuration file where the data entry fields are defined.  Configuration files (ending with a CFG file extension) may seem a bit complicated at first, and they must be written in a separate program (an ASCII text editor like NotePad or NotePad++ on Windows).  The effort of thinking through a configuration file, however, means thinking through the structure of your data before you start collecting it (unlike, for instance, if you use a spreadsheet), and this effort typically pays off later when you go to analyze the data.

Several example CFG files are included here in the CFGs folder, and here is a sample configuration file to illustrate some features:

```
[E5]
table=lithics

[ID]
input=text
prompt=Enter the artifact ID
unique=True

[ArtifactType]
input=menu
prompt=Select the artifact type
menu=Tool,Flake,Core

[ToolType]
input=menu
prompt=Select the tool type
menu=Scraper,Notch,Point,Other
condition1=ArtifactType Tool

[PlatformType]
input=menu
prompt=What is the platform
menu=Plain,Cortical,Missing,Other
condition1=ArtifactType Tool Flake

[PlatformWidth]
input=numeric
prompt=Measure the platform width
condition1=ArtifactType Tool Flake
condition2=PlatformType not Missing

[Weight]
input=numeric

```

The file is organized into blocks defined by the [].  Each file will have an [E5] block (usually at the start) that contains settings that apply to the whole configuration file.  In this example, there is one option (table=) which tells E5 what to call the database table.  If no table is specified, E5 uses '_default'.  Because it is not specified here, the database file itself (a JSON file) will have the same name as the configuration file.

Next is a series of data entry fields (again, each defined with []).  Here the first field is an artifact ID.  The 'type' option tells E5 what kind of data to accept.  Valid options include text, note, numeric, menus, boolean (True/False), and the date and time.  The *prompt* is specified with an option, and then the *unique* option tells E5 that each data record must have a unique value for this field.  Attempts to duplicate a value for this field will generate a warning, and if data entry continues it will edit (or overwrite) the previous record with this ID.

The *ArtifactType* field demonstrates the use of menus.  The actual menu items are specified in the *menu* option and are comma separated.  There is no limit to the number of menu items, and they are displayed in the order specified here (unless the *sorted* option is set to *True*).  The *ToolType* field that follows is also a menu, but it demonstrates the use of conditionals.  During data entry, the *ToolType* menu will only be displayed when *ArtifactType* is a tool, otherwise E5 will skip to the next field and insert an empty string ("") for the *ToolType* field.  

Likewise *PlatformType* is conditioned on the *ArtifactType* being a tool or a flake.  The field that follows, *PlatformWidth*, has two conditionals which must both be true otherwise the field will be skipped and an empty value will be inserted into the database table.  Notice that the second condition illustrates the use of the not keyword on conditions.  When the *PlatformType* is a value other than missing, this condition is true.

Both the *PlatformWidth* field and the last field, *Weight*, are numeric fields meaning that only valid numbers are accepted as input.  All other entries will generate an error and data entry cannot continue.

#### Installation  



#### Details

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

