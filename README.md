#  metatool

[![Build Status](https://travis-ci.org/Storj/metatool.svg?branch=master)](https://travis-ci.org/Storj/metatool)
[![Coverage Status](https://coveralls.io/repos/Storj/metatool/badge.svg?branch=master&service=github)](https://coveralls.io/github/Storj/metatool?branch=master)
[![License](https://img.shields.io/badge/license-AGPL%20License-blue.svg)](https://github.com/Storj/metatool/blob/master/LICENSE)

**metatool** is a console utility purposed for interact with the MetaDisk service.
It completely repeats all actions that you can perform with the MetaDisk
service through the "curl" terminal command, described at the <http://node2.metadisk.org/> page.

Below is the thorough specification for the metatool usage.

---

In general for running the application you may use the `metatool` terminal command with specified required arguments.
For help **information** run `metatool` without arguments or with `-h`, `-help`, `--help`:

    $ metatool
    ===========================================
    welcome to the metatool help information
    ===========================================

    usage:
    <-- the help information -->
    
---

Syntax for usage of **metatool** is:

    metatool <action> [ appropriate | arguments | for actions ] [--url URL_ADDRESS]
    
The first required argument after `metatool` is an **action**. Namely one of 
`audit`,`download`,`files`,`info`,`upload`, each for an appropriate task.
In example: 

    $ metatool info
    

The ``--url`` is the optional argument common for all the actions and defines
the URL-address of the *target server*:

    metatool info --url http://node2.metadisk.org/

This example in truth don't bring any obvious difference in results - by default the target server is **http://node2.metadisk.org/** as well.
You can either set an system *environment variable* **MEATADISKSERVER** to
provide target server instead of using the `--url` opt. argument.


All of the actions defines set of original required arguments.
Let us go through all of them!

---

There are two the most simple **actions** with no arguments after, but mentioned above optional ``--url``:


### `$ metatool files`

    $ metatool files
    200
    ["d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"]
       
This command outputs the *response code* - `200` and all *hash-names* of uploaded files -  
`"d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"`.

### `$ metatool info`

    metatool info
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

Such a command outputs the *response code* - `200` and a content of the json file with the data usage of nodes, capacity, and public key.

---

Other commands expect additional arguments after the `action`:

### `$ metatool upload <path_to_file> [-r | --file_role <FILE_ROLE>]`

This command is *upload* the __file__ specified like required positional argument into the server with the default value of __role__ - __`001`__:

    $ metatool upload README.md 
    201
    {
      "data_hash": "fcd533cd12aa8a9e9ffc7ee0f53198cf76da551e211aff85d2a2ef35639f99e9",
      "file_role": "001"
    }
    
Returned data is a printout of the *response code* - `201` and content of the json file with **data_hash** and **role** of the
uploaded file.

If you want to set the other value of **file_role** use optional argument -r or --file_role:

    $ metatool upload README.md --file_role 001
    201
    {
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695",
      "file_role": "001"
    }
    
Metatool allow you to define behavior and accessibility of the file, while the uploading to the server. 
The way to do this is to define the `file_role` mentioned above, which is the set of three significant numbers: 
    
    [ (0 / 1 / 2)  (0 / 1 / 2)  (0 / 1) ] 
       <payment>     <access>  <servable>

    +--------------------------------------------------------------------------+
    |       |                     sort of the meaning                          |
    | value |------------------------------------------------------------------|
    |       |       Payment         |           Access              | Servable |
    |-------+-----------------------+-------------------------------+----------|
    |  0    | Free                  | Anyone can access             |   False  |
    |  1    | Paid by downloader    | Specified users can access    |   True   |
    |  2    | Paid by owner         | Only owner can access         |  --//--  |
    +--------------------------------------------------------------------------+

1. **Payment value** - defines who must pay for the downloading.
2. **Access value** - defines who can access to the file on the server.
3. **Servable value** - defines whether the served data will be decrypted or not while the downloading. 
                        (It will be used only when decryption key is passed.)
    
### `$ metatool audit <data_hash> <challenge_seed>`

This **action** ensures the existence of files on the server.
It requires two positional arguments (both compulsory):

1. `file_hash` - hash-name of the file which you want to check out
2. `seed` - **__challenge seed__**, which is just a snippet of the data, purposed for generation a new original *hash-sum*
from **file** plus **seed**.

Be sure to put this arguments in the right order:

    $ metatool audit 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b
    201
    {
      "challenge_response": "46ca26590762503ebe34fb44728536e295da480dcdc260088524321721b6ad93",
      "challenge_seed": "19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b",
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695"
    }

Responce for the command is the *response code* - `201` and json with the data you was enter with the one additional item - 
**`challenge_response`** - the original **hash** mentioned above. You can compare it with an expected value.

### `$ metatool download <file_hash> [--decryption_key KEY] [--rename_file NEW_NAME] [--link]`

**download** action fetch the file from server. Here is one required argument - **`file_hash`** and two optional - 
**`--decryption_key`** and **`--rename_file`**.

* **`file_hash`** - hash-name of the needed file.
* **`--decryption_key`** - key for the decryption file.
* **`--rename_file`** - desired saving name (included path) of the downloaded file.
* **`--link`** -- will return the url GET request string instead of performing the downloading.
 
Below is the example of commands and explanation for it.

This command save the file at the current directory under the hash-name; return nothing in the console
while operation complete successfully, otherwise show an occured error:

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695
    
This's doing the same but saving decrypted file:

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --decryption_key=%A3%B4e%EA%82%00%22%3A%C3%86%C0hn1%B3%F7%F7%F8%8EL7S%F3D%28%7C%85%95%CE%9D%D5B

In this case it will set the downloaded file name:
    
    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file just_file.md

You can either indicate an relative and full path to the directory with this name:

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ../just_file.md
    
    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file ~/just_file.md
    
You can even fetch the **http request string** and perform the downloading in example through the browser by passing **--link** optional argument.
**metatool** will not than execute the downloading but just will generate the appropriate **URL** string:

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file just_file.md --link
    http://your.node.com/api/files/76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695?file_alias=just_file.md
    
> **_Note:_** Be careful with the choosing a name for saving - the program will rewrite files with the same name without warning!
