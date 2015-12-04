#  metatool

[![Build Status](https://travis-ci.org/Storj/metatool.svg?branch=master)](https://travis-ci.org/Storj/metatool)
[![Coverage Status](https://coveralls.io/repos/Storj/metatool/badge.svg?branch=master&service=github)](https://coveralls.io/github/Storj/metatool?branch=master)
[![License](https://img.shields.io/badge/license-AGPL%20License-blue.svg)](https://github.com/Storj/metatool/blob/master/LICENSE)

https://img.shields.io/github/license/storj/metatool.svg

metadisk.py is a console utility purposed for interact with the Metadisk service.
It completely repeat all actions that you can perform with the Metadisk
service through the "curl" terminal command, described at the <http://dev.storj.anvil8.com/> page.
> **_Note:_ metadisk.py** for running require Python3 interpreter and installed packages specified at the __setup.sh__

Below is the thorough specification for the metadisk.py usage.

---

In general for running the application you may use the `python3` terminal command with specified `metadisk.py` and required arguments.
For watching help **information** run `metadisk.py` without arguments or with `-h`, `-help`, `--help`:


    $ python3 metadisk.py
    ===========================================
    welcome to the metadisk.py help information
    ===========================================

    usage:
    <-- the help information -->
    
---

Common form of usage the **metadisk.py** is:

    python metadisk.py <action> [ appropriate | arguments | for actions ] [--url URL_ADDRESS]
    
The first required argument after `metadisk.py` is an **action**. Namely one of 
`audit`,`download`,`files`,`info`,`upload`, each for an appropriate task.
In example: 

    $ python3 metadisk.py info
    

The `--url` optional argument define url address of the *target server*:

    python metadisk.py info --url http://dev.storj.anvil8.com

This example in truth don't bring any obvious difference in results - by default the target server is **http://dev.storj.anvil8.com/** as well.
You can either set an system *environment variable* **MEATADISKSERVER** to
provide target server instead of using the `--url` opt. argument.


All of actions define set of original required arguments.
Let us go through all of them!

---

There are two the most simple **action** with no arguments after:


### `$ python3 metadisk.py files`

    $ python3 metadisk.py files
    200
    ["d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"]
       
This command outputs the *response code* - `200` and all *hash-names* of uploaded files -  
`"d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"`.

### `$ python3 metadisk.py info`

    python3 metadisk.py info
    200
    {
      "bandwidth": {
        "current": {
          "incoming": 0,
          "outgoing": 0
        },
        "limits": {
          "incoming": null,
          "outgoing": null
        },
        "total": {
          "incoming": 0,
          "outgoing": 0
        }
      },
      "public_key": "13LWbTkeuu4Pz7nFd6jCEEAwLfYZsDJSnK",
      "storage": {
        "capacity": 524288000,
        "max_file_size": 18,
        "used": 18
      }
    }

Such a command outputs the *response code* - `200` and a content of the json file with the data usage of nodes.

---

Other commands expect additional arguments after the `action`:

### `$ python3 metadisk.py upload <path_to_file> [-r | --file_role <FILE_ROLE>]`

This command is *upload* the __file__ specified like required positional argument into the server with the default value of __role__ - __`001`__:

    $ python3 metadisk.py upload README.md 
    201
    {
      "data_hash": "fcd533cd12aa8a9e9ffc7ee0f53198cf76da551e211aff85d2a2ef35639f99e9",
      "file_role": "001"
    }
    
Returned data is a printout of the *response code* - `201` and content of the json file with **data_hash** and **role** of the
uploaded file.

If you want to set the other value of **file_role** use optional argument -r or --file_role:

    $ python3 metadisk.py upload README.md --file_role 002
    201
    {
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695",
      "file_role": "002"
    }
    
### `$ python3 metadisk.py audit <data_hash> <challenge_seed>`

This **action** purposed for the ensure in an existence of files on the server (in opposite to the plain serving hashes of files).
It require two positional arguments (both compulsory):

1. `file_hash` - hash-name of the file which you want to check out
2. `seed` - **__challenge seed__**, which is just a snippet of the data, purposed for generation a new original *hash-sum*
from **file** plus **seed**.

Be sure to put this arguments in the right order:

    $ python3 metadisk.py audit 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b
    201
    {
      "challenge_response": "46ca26590762503ebe34fb44728536e295da480dcdc260088524321721b6ad93",
      "challenge_seed": "19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b",
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695"
    }

Responce for the command is the *response code* - `201` and json with the data you was enter with the one additional item - 
**`challenge_response`** - the original **hash** mentioned above. You can compare it with an expected value.

### `$ python3 metadisk.py download <file_hash> [--decryption_key KEY] [--rename_file NEW_NAME]`

**download** action fetch the file from server. Here is one required argument - **`file_hash`** and two optional - 
**`--decryption_key`** and **`--rename_file`**.

* **`file_hash`** - hash-name of the needed file.
* **`--decryption_key`** - key for the decryption file.
* **`--rename_file`** - desired saving name (included path) of the downloaded file.
 
Below is the example of commands and explanation for it.

This command save the file at the current directory under the hash-name; return nothing in the console
while operation complete successfully, otherwise show an occured error:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695


It's doing the same but saving decrypted file:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --decryption_key=%A3%B4e%EA%82%00%22%3A%C3%86%C0hn1%B3%F7%F7%F8%8EL7S%F3D%28%7C%85%95%CE%9D%D5B

Last case is the setting downloaded file name:
    
    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file just_file.md

You can either indicate an relative and full path to the directory with this name:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ../just_file.md
    
    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ~/just_file.md
    
> **_Note:_** Be careful with the choosing a name for saving - the program will rewrite files with the same name without warning!
