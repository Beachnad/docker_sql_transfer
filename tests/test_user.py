def kit_test_installation(pkg):
    def wrapper(host):
        pkg_obj = host.package(pkg)
        assert pkg_obj.is_installed
    return wrapper


def test_passwd_file(host):
    passwd = host.file("/etc/passwd")
    assert passwd.contains("root")
    assert passwd.user == "root"
    assert passwd.group == "root"
    assert passwd.mode == 0o644


def test_odbc_installation(host):
    lib_file = host.file("/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.1.1")
    assert lib_file.exists

    odbcinst_file = host.file("/opt/microsoft/msodbcsql17/etc/odbcinst.ini")
    assert odbcinst_file.exists
    assert odbcinst_file.contains("Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.1.1")


test_unixodbc_is_installed = kit_test_installation('unixodbc')
