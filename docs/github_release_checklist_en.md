# Mini Checklist for creating a GitHub release

## Before creating the tag

1. Verify that `VERSION` contains the correct version, for example `0.1.0`.
2. Confirm that all required changes are already in `main` or in the branch you are going to tag.
3. Run `git status` and make sure there are no uncommitted changes left.
4. Run `git push` and wait for GitHub Actions to finish successfully.

## Confirm the workflow

5. Check that these jobs pass in GitHub Actions:
   * `unit_tests`
   * `build_linux`
   * `test_linux`
   * `build_windows`
   * `test_windows`
   * `build_macos`
   * `test_macos`
6. Confirm that the Linux workflow is already configured to include these release assets:
   * `LucioIVACalculator`
   * `LucioIVACalculator.desktop`
   * `app-icon.svg`

## Create the tag

7. Create the tag with the `v` prefix using the same version as `VERSION`:

```bash
git tag v0.1.0
```

8. Push the tag to GitHub:

```bash
git push origin v0.1.0
```

## After pushing the tag

9. Wait for GitHub Actions to run again for the tag.
10. Verify that the `release` job runs.
11. Open the repository Releases section and confirm that the release was created.

## Check the release assets

12. Confirm that the release includes:
   * `LucioIVACalculator-<version>-setup.exe`
   * `LucioIVACalculator`
   * `LucioIVACalculator.desktop`
   * `app-icon.svg`
   * `LucioIVACalculator-<version>-macOS-x64.zip`

## If something fails

13. If the tag workflow fails, fix the problem, commit, and push.
14. Delete the local and remote tag only if you really need to recreate it:

```bash
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0
```

15. Then create and push the correct tag again.
