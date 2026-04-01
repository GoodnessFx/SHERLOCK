{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.sqlite
    pkgs.gcc
  ];
  env = {
    PYTHONPATH = ".:$PYTHONPATH";
  };
}
