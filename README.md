# Duplicity backup script

1. [Duplicity_backup_script](#duplicity-backup-script)
2. [Variables](#variables)
    1. [Ansible](#ansible)
    2. [Environment](#environment)
3. [Getting started](#getting-started)
4. [Testing](#testing)
5. [Authors and license](#authors-and-license)

The duplicity_backup Ansible role configures a backup script that creates encrypted backups according to a user-defined configuration. The script is based on Duplicity and uses GPG keypairs for encryption.

## Variables

### Ansible

* `limit_full` - controls the `--full-if-older-than` parameter and defines how frequently Duplicity creates a full backup
* `limit_retention` - controls the `remove-older-than` parameter and deletes all backup sets older than the given time
* `log_file` - controls the `--log-file` parameter and defines which file Duplicity writes logs to
* `user` - defines the user to whom the script creates a GPG keypair and to whose home directory this role deploys the backup script

### Environment

* `DPBX_ACCESS_TOKEN` - Dropbox access token that the script provides when a user executes it for the first time
* `DPBX_APP_KEY` - Dropbox app key that is specific to the owner of a Dropbox app
* `DPBX_APP_SECRET` - Dropbox app secret that is specific to the owner of a Dropbox app
* GPG_EMAIL - an email address that is associated with a GPG key
* `GPG_KEY` - the ID of the GPG pubring that this role creates
* `GPG_NAME` - the name of the user associated with a GPG key
* `PASSPHRASE` - a passphrase that protects the primary and subordinate GPG private keys

## Getting started

Create a file called `vars/user_config.yml` and define a personal backup configuration. The file should include a map structure as follows:

```
backup_map:
  - src: "/home/{{ user | default(ansible_user) }}/Documents"
    dest: Documents
    limit_full: 7D
    limit_retention: 14D

  - src: "/home/{{ user | default(ansible_user) }}/Music"
    dest: Documents
    limit_full: 30D
    limit_retention: 60D
```

The map structure may include as many sources as necessary. The parameter `src` defines the local path from which Duplicity uploads backups to a directory called `dest` within a Dropbox app. Parameters `limit_full` and `limit_retention` may be configured for each source individually.

Then export the known environment variables:

```
export DPBX_APP_KEY="..."
export DPBX_APP_SECRET="..."
export GPG_EMAIL="..."
export GPG_NAME="..."
export PASSPHRASE="..."
```

Now the role can be deployed against a targeted host:

```
ansible-playbook playbook.yml -e duplicity_backup_create_gpg_keypair=True
```

When the script is executed for the first time, a wizard instructs the user to configure access to a personal Dropbox app. Once the wizard finishes, export the missing environment variables:

```
export DPBX_ACCESS_TOKEN="..."
export GPG_KEY="..."
```

Finally, deploy the missing environment variables:

```
ansible-playbook playbook.yml -t duplicity_backup_define_environment_variables
```




## Testing

## Authors and license
