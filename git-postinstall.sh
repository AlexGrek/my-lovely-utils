#!/bin/bash

# --- Identity (Update these!) ---
# git config --global user.name "Your Name"
# git config --global user.email "you@example.com"

# --- The "Magic" Push (Your Request) ---
# Automatically setup remote tracking and push current branch.
# This eliminates the need for 'git push -u origin <branchname>'
# Requires Git 2.37+
git config --global push.autoSetupRemote true

# --- Modern Workflow Defaults ---
# Use 'main' instead of 'master' for new repositories
git config --global init.defaultBranch main

# Rebase on pull to keep a linear history (avoids messy merge commits on simple pulls)
git config --global pull.rebase true

# Automatically remove local references to remote branches that have been deleted
git config --global fetch.prune true

# --- Quality of Life ---
# Use VS Code as the editor (change 'code --wait' to 'vim' or 'nano' if preferred)
git config --global core.editor "code --wait"

# enhance the diff output with better syntax highlighting if available
git config --global core.pager "less -F -X"

# Correct typos in commands automatically after 1 second (e.g. 'git statsu' runs 'status')
git config --global help.autocorrect 10

# --- Essential Aliases ---
# Short and sweet status
git config --global alias.s "status"
# Quick checkout
git config --global alias.co "checkout"
# Quick commit
git config --global alias.ci "commit"
# Quick branch
git config --global alias.br "branch"
# A much better log view (graphical, colored, concise)
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
# 'git undo' to undo the last commit but keep changes in staging
git config --global alias.undo "reset --soft HEAD~1"

echo "Git configuration applied successfully!"
