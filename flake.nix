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
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.opencode
          pkgs.nodejs_22
          (pkgs.python3.withPackages (ps: with ps; [
            matplotlib
          ]))
          pkgs.git
        ];

        shellHook = ''
          # Add local scripts to PATH
          export PATH="$PWD/scripts:$PATH"
          # Add src to PYTHONPATH for src layout
          export PYTHONPATH="$PWD/src:$PYTHONPATH"
          echo "Dev AI shell"
          echo

          if [ -z "$OPENAI_API_KEY" ]; then
            echo "OPENAI_API_KEY is not set"
            echo "Set it with: export OPENAI_API_KEY=..."
          else
            echo "OPENAI_API_KEY is set"
          fi

          echo
          echo "Run OpenCode:"
          echo "  opencode"
          echo
          echo "Run OpenAI Codex CLI without installing globally:"
          echo "  npx @openai/codex"
          echo
        '';
      };
    };
}
