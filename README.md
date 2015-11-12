# Guide for metatool
metadisk.py is a console utility purposed for interact with Metadisk service.
It completely repeat all action that you can perform with Metadisk
service through the "curl" terminal command, described at the <http://dev.storj.anvil8.com/> page.
> **_Note:_ metadisk.py** for running require Python3 interpreter and installed packages specified at the __setup.sh__

Below is the thorough specification of metadisk.py usage.

---

In common for running application you may use `python3` terminal command with specified `metadisk.py` and required arguments.
For plain test run you can enter the following command in the terminal(in the same current directory as metadisk.py):


    $ python3 metadisk.py -h   
    usage: metadisk.py [-h] {audit,download,files,info,upload}
    
    positional arguments:
      {audit,download,files,info,upload}
    
    optional arguments:
      -h, --help            show this help message and exit
    

The first required argument after `metadisk.py` is an **action**. Namely one of 
`audit`,`download`,`files`,`info`,`upload`, each for appropriate task.
In example: 

    $ python3 metadisk.py info
    
Let us go through all of them.

---

There are two the most simple **action** with no argument after:


#### `$ python3 metadisk.py files`

    $ python3 metadisk.py files
    200
    ["d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"]
       
This command outputs *response code* - `200` and all *hash-names* of uploaded files -  
`"d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"`.

#### `$ python3 metadisk.py`

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

Such a command outputs *response code* - `200` and a content of json file with the data usage of nodes.

---

Other commands expect additional arguments after the `action`:

#### `$ python3 metadisk.py upload <path_to_file> [-r | --file_role <FILE_ROLE>]`

This command is *upload* __file__ specified like required positional argument into the server with default value of __role__ - __`001`__:

    $ python3 metadisk.py upload README.md 
    201
    {
      "data_hash": "fcd533cd12aa8a9e9ffc7ee0f53198cf76da551e211aff85d2a2ef35639f99e9",
      "file_role": "001"
    }
    
Returned data is printout of *response code* - `201` and content of json file with **data_hash** and **role** of
uploaded file.

If you want to set other value of **file_role** use optional argument -r or --file_role:

    $ python3 metadisk.py upload README.md --file_role 002
    201
    {
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695",
      "file_role": "002"
    }
    
#### `$ python3 metadisk.py audit <data_hash> <challenge_seed>`

This **action** purposed for ensure existence of files on the server (in opposite to plain serving hashes of files).
It require two positional arguments (both compulsory):

1. `file_hash` - hash-name of file which you want to check out
2. `seed` - **__challenge seed__**, which is just a snippet of data, purposed for generation new original *hash-sum*
from **file** plus **seed**.

Be sure to put this arguments in the right order:

    $ python3 metadisk.py audit 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b
    201
    {
      "challenge_response": "46ca26590762503ebe34fb44728536e295da480dcdc260088524321721b6ad93",
      "challenge_seed": "19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b",
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695"
    }

Responce for the command is *response code* - `201` and json with data you was enter with one additional item - 
**`challenge_response`** - the original **hash** mentioned above. You can compare it with expected value.

#### `$ python3 metadisk.py download <file_hash> [--decryption_key KEY] [--rename_file NEW_NAME]`

**download** action fetch file from server. Here is one required argument - **`file_hash`** and two optional - 
**`--decryption_key`** and **`--rename_file`**.

* **`file_hash`** - hash-name of needed file.
* **`--decryption_key`** - key for decryption file.
* **`--rename_file`** - desired saving name (included path) of downloaded file.
 
Below is the example of commands and explanation for it.

This command save file at the current directory under the hash-name; return nothing in the console
while operation complete successfully, otherwise show occured error:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695


It's doing the same but saving decrypted file:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --decryption_key=%A3%B4e%EA%82%00%22%3A%C3%86%C0hn1%B3%F7%F7%F8%8EL7S%F3D%28%7C%85%95%CE%9D%D5B

Last case is setting downloaded file name:
    
    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file just_file.md

You can either indicate relative and full path to directory with this name:

    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ../just_file.md
    
    $ python3 metadisk.py download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ~/just_file.md
    
> **_Note:_** Be careful with choosing name for saving - program will rewrite file with same name without warning!