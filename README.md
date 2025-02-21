# Personal Home Folder Scripts Collection
Might eventually combine with some AI function called tools as well.

## Ideas
- add a selected license file from the Ardea ones based on project type

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
- `path`: Provides some `PATH` management
- `tree`: Lists tree with dir sizes to dept 2
- `deep-tree`: Same as above but depth 4
- `find-junk`: Finds commonly .gitignore'd files/folders
- `clean-junk`: Deletes them
- `uncommitted`: Looks for repos with uncommited changes in current dir and sub dirs
- `fix-mode`: Fixes repos to not worry about file permission changes
- `commit-all`: Opens option to select repos to skip and then makes a --no-verify commit on all with message "YYYYMMDD commit for transfer"
  - Flag `--no-interactive` doesn't ask and just does the thing
- `nuke`: Runs `commit-all` then `clean-junk`






* Two ways to create the repo
   * Github template
   * CLI tool
* Using a GitHub App with webhooks
   * There will be a flag of wether to auto deploy on push to main or from a deploy button on the main SaaS page
   * In either case, the GitHub app runs validation on the Agents and Tools in the repo to make sure everything is set up correctly
* Right now we will just focus on tools and agents
   * Each will have its own dir in the repo
   * Tools will be composed into the each agent container if the agent has access to that tool
   * Agents will have a flag determining if they are ephemeral or not
      * ephemeral agents will live in a Cloud Run container
      * non-ephemeral will have their own GKE container in a cluster
      * each container will have a WebRTC service that connects will connect to both OpenAI realtime and the App frontend running from Firebase Storage (NextJS app)
      * Each agent from the repo will create its own deterministic ID that won't collide with Firebase document Ids
* The user should be able to create the repo, add the GitHub App from the marketplace, click deploy on the SaaS frontend, and have the agents and tools deploy to their already existing account (uses Firebase Auth) without overwriting any existing Tools or agents
* The non-ephemeral agents should show a running icon and have the option to be stopped or started
* the ephemeral agents should have the ability to be started
* The ephemeral agents should save their state on SIGTERM
* If the user has the auto-deploy option set and merges to main it should redeploy the agents and tools, overwriting themselves
* if the user hits deploy on the SaaS front-end the agents should redeploy overwriting themselves
