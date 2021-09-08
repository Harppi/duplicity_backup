import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

@pytest.mark.parametrize("name", [
    ("python3-venv"),
    ("python3-pip"),
    ("gettext"),
    ("librsync-dev"),
    ("haveged"),
])

def test_apt_prerequisites(host, name):
    pkg = host.package(name)
    assert pkg.is_installed

@pytest.mark.parametrize("name", [
    ("dropbox"),
    ("duplicity"),
])

def test_pip_prerequisites(host, name):
    pkgs = host.pip.get_packages(pip_path='/usr/bin/pip3')
    assert name in pkgs

# Ensure GPG keypair exists
def test_gpg_keypair(host):
    cmd = host.run("gpg --list-keys | grep root@root.com")
    assert cmd.succeeded == True

@pytest.mark.parametrize("gpg_dir_permissions", [
    ("/root/.gnupg/"),
    ("/root/.gnupg/private-keys-v1.d/"),
    ("/root/.gnupg/openpgp-revocs.d/"),
])

def test_gpg_permissions(host, gpg_dir_permissions):
    gpg = host.file(gpg_dir_permissions)
    assert gpg.exists
    assert gpg.user == "root"
    assert gpg.group == "root"
    assert gpg.mode == 0o700

# Ensure duplicity directory exists, permissions

# Ensure env vars file exists, permissions

# Ensure log directory exists, permissions

# Ensure backup and restoration scripts exist, permissions
