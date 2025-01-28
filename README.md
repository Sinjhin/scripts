# Personal Home Folder Scripts Collection
Might eventually combine with some AI function called tools as well.

## Usage
So, you know Python pretty well? It's nice and friendly isn't it?

Ever get frustrated with shell scripts?

Yeah, me too.

So, this allows you to use `conda`, `poetry`, `poethepoet` installed globally to run python files from a `~/scripts` dir with `p <script_name>`. It also allows you to use `poetry` within a `conda` venv of your choosing to modify that `~/scripts` project like `hp add torch`.

Neat, right?
Probably should have looked to see if anyone else had already done this.
🤷🏻‍♂️

## Requirements
Installed globally:
- conda
- poetry
- poethepoet

## Setup
- Clone this repo to your home dir:
  - `cd ~ && git clone git@github.com:Sinjhin/scripts.git`
- Add these functions to your `.zshrc`, `.bashrc`, etc..
  - (Replace `sinjhin` with whatever conda venv you want to use)
```shell
# runs Poe in ~/scripts from anywhere
function p() {
    CURRENT_DIR="$(pwd)" poe -C ~/scripts "$@"
}
# Sets specified conda venv and runs 'poetry ...args' from ~/scripts
function hp() {
    if ! conda info --envs | grep -q "^sinjhin "; then
        echo "Uh oh, can't find the 'sinjhin' environment."
        return 1
    fi

    eval "$(conda shell.zsh hook)" # Give conda the keys to the kingdom
    (conda activate sinjhin && cd ~/scripts && poetry "$@")
}
```
then source it: `source ~/.zshrc`

## Modules
- `p`: PoeThePoet. Looks at `~/scripts/pyproject.toml`'s `[tool.poe.tasks]`
- `hp`: Poetry. Runs `poetry ...args` from `~/scripts` in set conda venv

## Scripts
- `test`: Just prints something
- `ls`: Just shows a framework of what can be done with script locations for now
- `noncommital`: Checks current dir and sub-dirs for repos with uncommited changes and lists them