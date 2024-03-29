import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# Test if apt installed the required packages
@pytest.mark.parametrize("package", [
    ("python3-venv"),
    ("python3-pip"),
    ("gettext"),
    ("librsync-dev"),
    ("haveged"),
])
def test_apt_prerequisites(host, package):
    pkg = host.package(package)
    assert pkg.is_installed


# Test if pip3 installed the required packages
@pytest.mark.parametrize("package", [
    ("dropbox"),
    ("duplicity"),
])
def test_pip_prerequisites(host, package):
    pkgs = host.pip.get_packages(pip_path='/usr/bin/pip3')
    assert package in pkgs


# Test if a certain GPG keypair exists
def test_gpg_keypair(host):
    cmd = host.run("gpg --list-keys | grep restore@root.com")
    assert cmd.succeeded is True


# Test if GPG directories exist and if their permissions are correct
@pytest.mark.parametrize("gpg_dir", [
    ("/root/.gnupg/"),
    ("/root/.gnupg/private-keys-v1.d/"),
    ("/root/.gnupg/openpgp-revocs.d/"),
])
def test_gpg_permissions(host, gpg_dir):
    gpg_dir = host.file(gpg_dir)
    assert gpg_dir.exists
    assert gpg_dir.user == "root"
    assert gpg_dir.group == "root"
    assert gpg_dir.mode == 0o700


# Test if duplicity directories and files exist and if their permissions are
# correct
@pytest.mark.parametrize("duplicity_dirs", [
    ("/root/.duplicity"),
    ("/root/.duplicity/.backup.sh"),
    ("/root/.duplicity/.restore.sh"),
    ("/var/log/duplicity")
])
def test_duplicity_permissions(host, duplicity_dirs):
    duplicity_dir = host.file(duplicity_dirs)
    assert duplicity_dir.exists
    assert duplicity_dir.user == "root"
    assert duplicity_dir.group == "root"
    assert duplicity_dir.mode == 0o700

    env_var_conf = host.file("/root/.duplicity/.env_variables.conf")
    assert env_var_conf.exists
    assert env_var_conf.user == "root"
    assert env_var_conf.group == "root"
    assert env_var_conf.mode == 0o600


# Test if log rotation works
@pytest.mark.parametrize("line", [
    ("/var/log/duplicity/duplicity_backup.log"),
    ("rotate 30"),
    ("daily"),
    ("compress"),
    ("missingok"),
    ("notifempty")
])
def test_log_rotation(host, line):
    log_rotation_conf = host.file("/etc/logrotate.d/duplicity")
    assert log_rotation_conf.exists
    assert log_rotation_conf.user == "root"
    assert log_rotation_conf.group == "root"
    assert log_rotation_conf.mode == 0o644
    assert log_rotation_conf.contains(line)

    cmd = host.run("logrotate -vf /etc/logrotate.d/duplicity")
    assert cmd.succeeded is True


# Test if .env_variables.conf includes correct lines
@pytest.mark.parametrize("line", [
    ('export DPBX_ACCESS_TOKEN="test_token"'),
    ('export DPBX_APP_KEY="test_key"'),
    ('export DPBX_APP_SECRET="test_secret"'),
    ('export GPG_KEY=""'),
    ('export PASSPHRASE="test_passphrase"')
])
def test_env_var_values(host, line):
    env_var_conf = host.file("/root/.duplicity/.env_variables.conf")
    assert env_var_conf.contains(line)
