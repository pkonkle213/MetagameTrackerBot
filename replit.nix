{pkgs}: {
  deps = [
    pkgs.openssl
    pkgs.python312Packages.pytest
    pkgs.cacert
    pkgs.postgresql
  ];
}
