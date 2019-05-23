# ansible-storedsafe-client

ansible-storedsafe-client.py is an ansible vault password client script, to be used for retrieving password from StoredSafe to be used for encryption and decryption when using ansible-vault.

##### The added benefits are

- User do not have to copy and paste password from StoredSafe
- Every retrieval of passwords to decrypt ansible-vault files or variables will be recorded in the StoredSafe audit log

The script is written in Python v2 and has been tested on macOS Sierra and on Linux (any fairly recent version of Ubuntu or Red Hat should work fine).

It is also possible to use the StoredSafes ansible lookup module ([ansible-storedsafe](https://github.com/storedsafe/ansible-storedsafe)), if you, for any reason, do not want to use ansible-vault for storing sensitive information.

## Installation instructions

This script requires Python v2 and some libraries. 

It has been developed and tested using Python v2.7.10, on macOS Mojave 10.14.4.

Most of the required libraries are installed by default, but requests require manual installation. 

**requests:**
```
sudo -H pip install requests
```

## Syntax

```
$ vault-storedsafe-client.py --help
 --verbose                  (Boolean) Enable verbose output.
 --debug                    (Boolean) Enable debug output.
 --vault-id <Object-ID>     Obtain the decrypted password from the object with the matching Object-ID (exact match, integer).
 --vault-id <String>        Search for the string, return decrypted password field from last matching object.

Obtain the decrypted password for the specified Object-ID (919) from StoredSafe.

$ ./vault-storedsafe-client.py --vault-id 919
f0m2dDOgZJaFMeVDVi0auYdrUwQA5QyWrBX2Rcdn

Search all available vaults for hostname or user matching the search string and return decrypted password from last matching object.

$ ./vault-storedsafe-client.py --vault-id prod-sweden-vars
81Fb6GlZIhTYOJeCncU3D9Z2gc3XfzyLSAF2bJOc
```

```
--verbose
``` 
> Add verbose output.

```
--debug
```
> Add debug output.

```
--vault-id <string>
```
> Search for string in StoredSafe and match it against host or username fields in any template having those fields and return the decrypted password.

```
--vault-id <object-id>
```
> Returns the decrypted password field for any template having an encrypted password with the exact Object-ID.

Usage
=====
vault-storedsafe-client.py utilises StoredSafe's REST API to lookup passwords in StoredSafe to encrypt files and/or variables for ansible-vault. 

vault-storedsafe-client.py requires that pre-authentication has been performed by the StoredSafe token handler CLI module ([storedsafe-tokenhandler.py](https://github.com/storedsafe/tokenhandler)) and stored in the init file ~/.storedsafe-client.rc.

#### To create an encrypted file
Search for any object matching the string ```prod-sweden-config``` against the hostname or user field in StoredSafe and use the password to encrypt the file.

```
$ cat moo.yml
---
- name: cow power!
  hosts: 127.0.0.1
  connection: local

  tasks:
  - name: Got milk?
    debug:
      msg: mooOOooo0000oooo

$ ansible-vault --vault-id=prod-sweden-config@vault-storedsafe-client.py encrypt moo.yml
$ cat moo.yml
$ANSIBLE_VAULT;1.2;AES256;prod-sweden-config
61623236633434383561336635323634386330386163386262373839643163646533626663613761
3766633637346235333265373139343763663538643665650a306662613835636635636338326435
37613461363730626236343632393865393833316431326264393237616532396534313439353561
3061656464646334330a303864363938386536366561663234643863643566386634376431313530
37366635323438303764303738656232353034613462633238303961653936626265
```
#### To view an encrypted file
Search for any object matching the string ```prod-sweden-config``` against the hostname or user field in StoredSafe and use the password to decrypt the file.

```
$ ansible-vault --vault-id=prod-sweden-config@vault-storedsafe-client.py view moo.yml
---
- name: cow power!
  hosts: 127.0.0.1
  connection: local

  tasks:
  - name: Got milk?
    debug:
      msg: mooOOooo0000oooo
```

#### To create an encrypted variable
Search for any object matching the string ```prod-sweden-vars``` against the hostname or user field in StoredSafe and use the password to encrypt the variable ```new_user_password```.

```
$ ansible-vault encrypt_string --vault-id=prod-sweden-vars@vault-storedsafe-client.py --stdin-name 'new_user_password'
Reading plaintext input from stdin. (ctrl-d to end input)
mooOOooo0000oooo
new_user_password: !vault |
          $ANSIBLE_VAULT;1.2;AES256;prod-sweden-vars
          34366563616464333638333265326231363137666363326561643230303762376133656338373334
          6436643631663465346165303662306338316137376136340a653961396633613135613265336233
          34666334306239623239666465613135396631326661633561623366393839653833303361623363
          6334643365666565640a373434363564316135663238356632623662623535653538333365656536
          38373135653465643565343165303364353961633338343538393564396436663234
Encryption successful
```

Search for any object matching the string ```prod-sweden-config``` against the hostname or user field in StoredSafe and use the password to decrypt files or variables when running the playbook ```moo.yml```.

```
$ ansible-playbook --vault-id=prod-sweden-config@vault-storedsafe-client.py moo.yml

PLAY [cow power!] ***************************************************************

TASK [Gathering Facts] **********************************************************
ok: [127.0.0.1]

TASK [Got milk?] ****************************************************************
ok: [127.0.0.1] => {
    "msg": "mooOOooo0000oooo"
}

PLAY RECAP **********************************************************************
127.0.0.1                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Limitations / Known issues

- If a search matches multiple secrets in StoredSafe, vault-storedsafe-client.py will return the last one found. If this is an issue, specify the numerical Object-ID.
- It would be nice to be able to search for any field in any StoredSafe template. However, too little information, just the vault-id, is passed to the client script to make that feasible.

## See also

- [https://docs.ansible.com/ansible/latest/user_guide/vault.html](https://docs.ansible.com/ansible/latest/user_guide/vault.html)

## License
AGPLv3
