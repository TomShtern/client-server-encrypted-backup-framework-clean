# Working with push protection from the command line

This document explains how to handle a blocked push from the command line when secret scanning detects a secret in your changes.

## About push protection from the command line

Push protection is a feature that prevents you from accidentally committing secrets to a repository. When you try to push a supported secret to a repository with push protection enabled, GitHub will block the push. You will see a message on the command line, and you can either remove the secret from your branch or follow a provided URL to see options for allowing the push. Up to five detected secrets are displayed at a time.

## Resolving a blocked push

To resolve a blocked push, you need to remove the secret from all commits where it appears.

### Removing a secret introduced by the latest commit on your branch

If the blocked secret was introduced in your most recent commit, follow these steps:
1. Remove the secret from your code.
2. To commit the changes, run `git commit --amend --all`. This updates the original commit instead of creating a new one.
3. Push your changes with `git push`.

### Removing a secret introduced by an earlier commit on your branch

If the secret is in an earlier commit, you will need to perform an interactive rebase:
1. Examine the error message to identify all commits containing the secret.
2. Use `git log` to view the commit history and find the earliest commit with the secret.
3. Start an interactive rebase with `git rebase -i <COMMIT-ID>~1`, replacing `<COMMIT-ID>` with the ID of the earliest commit containing the secret.
4. In the editor, change `pick` to `edit` for the commit you need to fix.
5. Remove the secret from your code.
6. Stage your changes with `git add .`.
7. Amend the commit with `git commit --amend`.
8. Continue the rebase with `git rebase --continue`.
9. Push your changes with `git push`.

## Bypassing push protection

If you believe a secret is safe to push, you may be able to bypass the block. When you allow a secret to be pushed, an alert is created in the "Security" tab. Depending on the reason you provide for the bypass, the alert may be automatically closed or remain open.

To bypass the block:
1. Visit the URL provided by GitHub in the command line error message.
2. Choose the reason for bypassing the block:
    * It's used in tests.
    * It's a false positive.
    * I'll fix it later.
3. Click "Allow me to push this secret."
4. Re-attempt the push from the command line within three hours.

## Requesting bypass privileges

If you can't bypass the block directly, you can request permission to do so.
1. Visit the URL from the error message.
2. Under "Or request bypass privileges," add a comment explaining your reasoning.
3. Click "Submit request."
4. You will receive an email notification about the decision. If approved, you can push the commit; if denied, you must remove the secret.

## Further reading

* Working with push protection in the GitHub UI
* Working with push protection from the REST API