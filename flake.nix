{
  description = "Dev shell with OpenCode, Codex CLI support, and Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system} = {
        default = pkgs.mkShell {
          packages = [
            pkgs.opencode
            pkgs.nodejs_22
            pkgs.git
            (pkgs.python3.withPackages (ps: with ps; [ matplotlib ]))
          ];

          shellHook = ''
            export PATH="$PWD/scripts:$PATH"
            export PYTHONPATH="$PWD/src"
            echo "Dev AI shell"
          '';
        };

        python = pkgs.mkShell {
          packages = [
            (pkgs.python3.withPackages (ps: with ps; [ matplotlib ]))
          ];
          shellHook = ''
            export PYTHONPATH="$PWD/src"
          '';
        };
      };
    };
}
