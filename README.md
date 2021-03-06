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
For help **information** run `metatool` without arguments or with `-h` / `--help`:

    $ metatool
    usage: METATOOL [-h] {audit,download,upload,files,info} ...
    
    This is the console app intended for interacting with the MetaCore server.
    
    positional arguments:
    ...
    
---

Syntax for usage of **metatool** is:

    metatool <action> [ appropriate | arguments | for actions ] [--url URL_ADDRESS]

The first required argument after `metatool` is an **action**. Namely, one of
`audit`,`download`,`files`,`info`,`upload`; each for an appropriate task.
In example: 

    $ metatool info
    

The `--url` is the optional argument, common for all of the actions. It defines
the URL-address of the *target server*:

    $ metatool info --url http://node2.metadisk.org/

This example in truth don't bring any obvious difference in results - by default the target server is **http://node2.metadisk.org/** as well.
You can either set an system *environment variable* **MEATADISKSERVER** to
provide target server instead of using the `--url` opt. argument.


Any of the actions has a set of distinct required arguments.
Let us go through all of them!

---

There are two the most simple **actions** with no arguments after, but mentioned above optional `--url`:


### `$ metatool files`

    $ metatool files
    200
    ["d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"]
       
This command outputs the *response code* - `200` and all *hash-names* of uploaded files -  
`"d4a9cbadec60988e1da65ed7af31c538abada9cd663d7ac3091a00479e57ad5a"`.

### `$ metatool info`

    $ metatool info
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

### `$ metatool upload`

    metatool upload <path_to_file> [-r | --file_role <FILE_ROLE> ] [--encrypt]


The **encrypted file** is preferred, but not forced, way to serve files on the MetaCore server, so uploading supports the **encryption**.

Next command uploads your **file**, specified as first and required positional argument, into the server
with the default value of `file_role` - **001**:

    $ metatool upload README.md
    201
    {
      "data_hash": "fcd533cd12aa8a9e9ffc7ee0f53198cf76da551e211aff85d2a2ef35639f99e9",
      "file_role": "001"
    }

Returned data is a printout of the *response code* - `201` and content of the json file with **data_hash** and **role** of the
uploaded file.

Put the `--encrypt` key to encrypt the sent data (your local file remains the same) and get the `decryption_key`:

    $ metatool upload README.md --encrypt --url http://localhost:5000
    201
    {
      "data_hash": "0c50ca846cba1140c1d1be3bdd1f9c10efed6e2692889e8520c73b96a548e998",
      "decryption_key": "5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57",
      "file_role": "001"
    }

Now you've got an additional item in the returned JSON - `decryption_key`. This is an "hexadecimalised" value of the bytes
`decryption_key` value. If you need the original bytes value, use the `binascii.unhexlify()` standard library function:

    >>> import binascii
    >>> binascii.unhexlify("5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57")
    '[\xfcX\x95.\xfa\x86\xa8\x9a\xb8\x9c\xf6\xb6\x05\xc9\xb8\xbf\xcd\x08\xd9\xb4N`p\xe7ai\x1c\xa1\xed+W'

If you want to set the other value of **file_role** use optional argument `-r` or `--file_role`:

    $ metatool upload README.md --file_role 011
    201
    {
      "data_hash": "76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695",
      "file_role": "011"
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
                        (it will be used only when decryption key is passed)

Under the above guidelines we create PAS codes to determine how a file is treated.
For example, **001** would be a free public file that can be downloaded in plaintext.

### `$ metatool audit`

Common usage:

    $ metatool audit <data_hash> <challenge_seed>

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

Response for the command is the *response code* - `201` and json with the data you was enter with the one additional item - 
**`challenge_response`** - the original **hash** mentioned above. You can compare it with an expected value.

### `$ metatool download`

Common usage:

    $ metatool download <file_hash> [--decryption_key "KEY"] [--rename_file NEW_NAME] [--link]

**download** action fetches the file from server. Here is one required argument - **`file_hash`** and two optional -
**`--decryption_key`** and **`--rename_file`**:

* **`file_hash`** - hash-name of the needed file.
* **`--decryption_key`** - key to the decryption of file in the **hexlify** bytes representation.
* **`--rename_file`** - desired saving name (included path) of the downloaded file.
* **`--link`** -- will return the url GET request string instead of performing the downloading.
 
Below is the example of commands and explanation for it.

This command saves the file at the current directory under the hash-name by default; returns the full path of downloaded file in the console
if this operation is completed successfully, otherwise shows an occurred error:

    $ metatool download 1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645
    /home/user/1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645

This does the same but saves **decrypted** file:

    $ metatool download 0c50ca846cba1140c1d1be3bdd1f9c10efed6e2692889e8520c73b96a548e998 \
    > --decryption_key 5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57
    /home/jeka/PycharmProjects/anvil8/storj/metatool/0c50ca846cba1140c1d1be3bdd1f9c10efed6e2692889e8520c73b96a548e998

In this case it will set up a new name for the downloaded file:

    $ metatool download 1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645 \
    > --rename_file just_file.txt
    /home/user/just_file.txt

You can either indicate a relative or full path to the directory with this name to save it:

    $ cd some_dir
    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 \
    > --rename_file ../just_file.txt
    /home/user/just_file.txt

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 \
    > --rename_file /home/user/download/just_file.txt
    /home/user/download/just_file.txt


You can even fetch the **http request string** and perform the downloading, in example through
the browser, by passing ``--link`` optional argument.
**metatool** than will not execute the downloading, but will generate the appropriate **URL** string::

    $ metatool download 76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695 --rename_file just_file.txt --link
    http://your.node.com/api/files/76cc2d5c077f440c8a422bec61070e3383807205845c8f6f22beeb28002ed695?file_alias=just_file.md

> **_Note:_** Be careful with the choosing a name for saving - the program will rewrite files with the same name without warning!
