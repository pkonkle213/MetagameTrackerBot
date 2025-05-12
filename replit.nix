{pkgs}: {
  deps = [
    pkgs.python312Packages.pytest
    pkgs.cacert
    pkgs.postgresql
  ];
}
