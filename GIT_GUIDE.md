# Git Quick Guide — Beyond Commit & Push

You know `git add`, `git commit`, `git push`. Here's what else matters.

---

## 1. The Three Areas

```
Working Directory  →  Staging Area  →  Local Repo  →  Remote (GitHub)
     (your edits)      (git add)      (git commit)    (git push)
```

- **Working directory**: Your actual files. Edit anything.
- **Staging area**: What you've chosen to include in the next commit (`git add`).
- **Local repo**: Commits on your machine (`git commit`).
- **Remote**: GitHub/other server (`git push`).

---

## 2. Branches — The Big Idea

A **branch** is a separate line of commits. `main` is the default.

- **Why use branches?** Work on features or experiments without touching `main`.
- **Flow**: Create branch → make commits → merge back into `main` when done.

### Essential Branch Commands

| Command | What it does |
|--------|----------------|
| `git branch` | List local branches (current has `*`) |
| `git branch -a` | List all (local + remote) |
| `git branch feature-x` | Create new branch (doesn't switch) |
| `git checkout feature-x` | Switch to `feature-x` |
| `git checkout -b feature-x` | Create *and* switch in one step |
| `git merge feature-x` | Merge `feature-x` into current branch |
| `git branch -d feature-x` | Delete branch (after merge) |

### Typical Workflow

```bash
# Start a new feature
git checkout -b add-bigquery-support

# Work, commit, commit...
git add .
git commit -m "Add BigQuery loader"
# ... more commits ...

# Merge back into main
git checkout main
git merge add-bigquery-support

# Clean up
git branch -d add-bigquery-support
git push
```

---

## 3. Syncing With Remote

| Command | What it does |
|--------|----------------|
| `git pull` | Fetch + merge remote changes into your branch |
| `git fetch` | Download remote updates (doesn't merge) |
| `git push origin main` | Push `main` to `origin` |
| `git push -u origin my-branch` | Push branch and set upstream (first time) |

**Best practice**: Run `git pull` before you start work so you have the latest changes.

---

## 4. Undoing Things

| Situation | Command |
|-----------|---------|
| Discard changes in a file (before commit) | `git restore filename` |
| Unstage a file | `git restore --staged filename` |
| Undo last commit, keep changes | `git reset --soft HEAD~1` |
| Undo last commit, discard changes | `git reset --hard HEAD~1` (careful!) |
| View what changed | `git diff` (unstaged), `git diff --staged` (staged) |

---

## 5. Inspecting History

| Command | What it does |
|--------|----------------|
| `git log` | Show commit history |
| `git log --oneline -10` | Short log, last 10 commits |
| `git status` | Working dir + staging status |
| `git diff` | See unstaged changes |

---

## 6. Remote Basics

| Command | What it does |
|--------|----------------|
| `git remote -v` | List remotes (usually `origin`) |
| `git clone <url>` | Copy repo to new folder |
| `git push` | Push to default remote/branch |
| `git pull` | Pull from default remote/branch |

---

## 7. One-Liner Cheat Sheet

```bash
git status                    # What's changed?
git add -A                     # Stage everything
git commit -m "message"       # Commit
git push                       # Send to GitHub
git pull                       # Get latest
git checkout -b new-branch     # New branch + switch
git merge other-branch         # Merge into current
git log --oneline -5           # Recent commits
git restore file               # Discard file changes
```

---

## 8. When Things Go Wrong

**Merge conflict**: Two people changed the same lines. Git marks conflicts in files with `<<<<<<<`, `=======`, `>>>>>>>`. Edit to fix, then `git add` and `git commit`.

**Accidentally committed to main**: Create branch from current state, reset main:
```bash
git branch my-work
git reset --hard origin/main   # main back to remote state
git checkout my-work            # continue on your branch
```

**Need to update remote branch list**: `git fetch --prune`
