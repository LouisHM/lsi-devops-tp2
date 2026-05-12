import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_nginx_running_and_enabled(host):
    app_service = host.service("nginx")
    assert app_service.is_running
    assert app_service.is_enabled


def test_nginx_listening(host):
    assert host.socket("tcp://0.0.0.0:8080").is_listening


def test_nginx_app_proxy_listening(host):
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_mysql_running_and_enabled(host):
    mysql_service = host.service("mysql")
    assert mysql_service.is_running
    assert mysql_service.is_enabled


def test_mysql_listening(host):
    assert host.file("/var/run/mysqld/mysqld.sock").exists


def test_app_service_running_and_enabled(host):
    app_service = host.service("devops-app")
    assert app_service.is_running
    assert app_service.is_enabled


def test_app_listening(host):
    assert host.socket("tcp://0.0.0.0:5000").is_listening


def test_app_http_response(host):
    cmd = host.run("curl -sf http://127.0.0.1:5000/")
    assert cmd.rc == 0
    assert "Hello DevOps" in cmd.stdout


def test_maildev_service_running_and_enabled(host):
    maildev_service = host.service("maildev")
    assert maildev_service.is_running
    assert maildev_service.is_enabled


def test_maildev_smtp_listening(host):
    assert host.socket("tcp://0.0.0.0:1025").is_listening


def test_maildev_web_listening(host):
    assert host.socket("tcp://0.0.0.0:1080").is_listening


def test_postfix_service_running_and_enabled(host):
    postfix_service = host.service("postfix")
    assert postfix_service.is_running
    assert postfix_service.is_enabled


def test_postfix_smtp_listening(host):
    assert host.socket("tcp://127.0.0.1:25").is_listening


def test_backup_script_exists(host):
    assert host.file("/usr/local/bin/devops-backup.sh").exists
    assert host.file("/usr/local/bin/devops-backup.sh").mode == 0o750


def test_backup_directory_exists(host):
    assert host.file("/var/backups/devops").is_directory


def test_backup_cron_scheduled(host):
    crontab = host.run("crontab -l -u root")
    assert "devops-backup.sh" in crontab.stdout
