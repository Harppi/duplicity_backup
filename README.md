# Duplicity backup script

1. [Duplicity_backup_script](#duplicity-backup-script)
2. [Variables](#variables)
    1. [Ansible](#ansible)
    2. [Environment variables](#environment-variables)
3. [Getting started](#getting-started)
    1. [Creating a Dropbox app](#creating-a-dropbox-app)
    2. [Defining user specific settings](#defining-user-specific-settings)
4. [Deploying the backup script](#deploying-the-backup-script)
5. [Restoring a backup](#restoring-a-backup)
6. [Testing](#testing)
7. [License](#authors-and-license)

The `duplicity_backup` Ansible role configures a backup script that creates encrypted backups according to a user-defined configuration. The script is based on Duplicity and uses GPG keypairs for encryption.

## Variables

### Ansible

* `limit_full` - controls the `--full-if-older-than` parameter and defines how frequently Duplicity creates a full backup
* `limit_retention` - controls the `remove-older-than` parameter and deletes all backup sets older than the given time
* `log_file` - controls the `--log-file` parameter and defines which file Duplicity writes logs to
* `user` - defines the user to whom the script creates a GPG keypair and to whose home directory this role deploys the backup script

### Environment variables

* `DPBX_ACCESS_TOKEN` - Dropbox access token that the script provides when a user executes the script for the first time
* `DPBX_APP_KEY` - Dropbox app key that is specific to the owner of a Dropbox app
* `DPBX_APP_SECRET` - Dropbox app secret that is specific to the owner of a Dropbox app
* `GPG_EMAIL` - an email address that is associated with a GPG key
* `GPG_KEY` - the ID of the GPG pubring that this role creates
* `GPG_NAME` - the name of the user associated with a GPG key
* `PASSPHRASE` - a passphrase that protects the primary and subordinate GPG private keys

## Getting started

The configuration of the script splits into two parts - creating a Dropbox application and defining user specific settings.

### Creating a Dropbox app

Navigate to Dropbox App console and create a new app. Choose `Scoped access` as the API, `App folder` as the type of access and name the app. Then navigate to the Permissions tab of the app and tick the `files.metadata.write`, `files.content.write` and `files.content.read` checkboxes.

### Defining user specific settings

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

Then export the known environment variables. Dropbox app key and app secret can be copied from Dropbox App Console, and GPG email, name and passphrase can be defined to one's liking.

```
export DPBX_APP_KEY="..."
export DPBX_APP_SECRET="..."
export GPG_EMAIL="..."
export GPG_NAME="..."
export PASSPHRASE="..."
```

## Deploying the backup script

Deploy the role against a targeted host:

```
ansible-playbook path/to/playbook.yml -e duplicity_backup_create_gpg_keypair=True -e ansible_python_interpreter=/usr/bin/python3
```

When the script is executed for the first time, a wizard instructs the user to configure access to a personal Dropbox app. Once the wizard finishes, export the missing environment variables:

```
export DPBX_ACCESS_TOKEN="..."
export GPG_KEY="..."
```

`GPG_KEY`, i.e. the public key, can be shown as follows:

```
alice% gpg --list-keys
/users/alice/.gnupg/pubring.gpg
---------------------------------------
pub  1024D/BB7576AC 1999-06-04 Alice (Judge) <alice@cyb.org>
sub  1024g/78E9A8FA 1999-06-04
```


Finally, re-deploy the configuration file that includes the environment variables:

```
ansible-playbook path/to/playbook.yml -t duplicity_backup_define_environment_variables
```

The backup script reads these variables in order to encrypt backups and authenticate against Dropbox. Store the GPG keypair in a secure place to be able to restore and decrypt existing backups in case of a system failure.

## Restoring a backup

Copy an existing GPG key pair to an arbitrary directory, define the path to the directory and deploy the role against a targeted host:

```
ansible-playbook path/to/playbook.yml -e gpg_key_path=path/to/gpg_key_pair
```

The role deploys the restoration script to `/home/user/.duplicity/restore.sh` where `user` equals to `REMOTE_USER`. The user can be defined by using option `-u` or `--user`.

Restore a backup executing the restoration script:

```
./restore.sh <source> <destination>
```

where `source` is the name of a directory within a Dropbox app that will be restored and `destination` is the local directory to which the script restores the contents of the directory.

## Testing

Testing requires Docker to be installed and running. Navigate into the root directory of the role and execute one of the following.

Converge the default instance and configure a brand new backup setup:

```
molecule converge
```

Converge a restoration instance, configure a backup setup and restore an
existing GPG keypair:

```
molecule converge --scenario-name restore
```

Investigate the internals of a Docker container:

```
molecule login
```

Run verification tests for a brand new backup setup:

```
molecule verify
```

Run verification tests for a restored backup setup:

```
molecule verify --scenario-name restore
```

Destroy instances:

```
molecule destroy
```

## License

MIT