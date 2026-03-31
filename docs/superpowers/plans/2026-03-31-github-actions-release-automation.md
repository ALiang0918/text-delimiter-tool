# GitHub Actions Release Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tag-triggered GitHub Actions workflow that validates version alignment, runs tests, builds the Windows executable, and publishes it to the matching GitHub Release automatically.

**Architecture:** Add a single Windows-based GitHub Actions workflow at `.github/workflows/release.yml` that reuses the existing PowerShell build script instead of duplicating packaging logic in YAML. The workflow will gate release publication behind a version-consistency check and existing Python unit tests, then upload `dist/TextDelimiterTool.exe` to the tag's release.

**Tech Stack:** GitHub Actions, PowerShell, Python 3.13, PyInstaller, existing repository build script

---

### Task 1: Add The Release Workflow Skeleton

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create the workflow file with tag trigger, permissions, and Windows runner**

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  release:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
```

- [ ] **Step 2: Verify the new workflow file exists locally**

Run: `powershell -Command "Test-Path '.github/workflows/release.yml'"`
Expected: `True`

- [ ] **Step 3: Commit the skeleton workflow**

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow skeleton"
```

### Task 2: Add Version Alignment Validation

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add a step that compares pushed tag version to the VERSION file**

```yaml
      - name: Validate tag matches VERSION
        shell: pwsh
        run: |
          $tag = "${{ github.ref_name }}"
          if (-not $tag.StartsWith('v')) {
            throw "Release tag must start with 'v'. Got: $tag"
          }

          $tagVersion = $tag.Substring(1)
          $fileVersion = (Get-Content VERSION -Raw).Trim()

          if ([string]::IsNullOrWhiteSpace($fileVersion)) {
            throw "VERSION file is empty."
          }

          if ($tagVersion -ne $fileVersion) {
            throw "Tag version '$tagVersion' does not match VERSION '$fileVersion'."
          }
```

- [ ] **Step 2: Review the workflow file and confirm the validation step appears before tests and build**

Run: `powershell -Command "Get-Content '.github/workflows/release.yml'"`
Expected: the `Validate tag matches VERSION` step appears before the unit-test steps

- [ ] **Step 3: Commit the version validation update**

```bash
git add .github/workflows/release.yml
git commit -m "ci: validate release tag version"
```

### Task 3: Add Test Execution And Build Steps

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add dependency installation, unit tests, and build execution steps**

```yaml
      - name: Install PyInstaller
        shell: pwsh
        run: python -m pip install pyinstaller

      - name: Run formatter tests
        shell: pwsh
        run: |
          $env:PYTHONPATH = 'src'
          python -m unittest tests.test_formatter -v

      - name: Run version tests
        shell: pwsh
        run: |
          $env:PYTHONPATH = 'src'
          python -m unittest tests.test_version -v

      - name: Build Windows executable
        shell: pwsh
        run: powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean
```

- [ ] **Step 2: Run the existing local verification commands to confirm the repository still passes the same checks used by the workflow**

Run: `powershell -Command "$env:PYTHONPATH='src'; python -m unittest tests.test_formatter -v"`
Expected: `OK`

Run: `powershell -Command "$env:PYTHONPATH='src'; python -m unittest tests.test_version -v"`
Expected: `OK`

- [ ] **Step 3: Commit the workflow test and build steps**

```bash
git add .github/workflows/release.yml
git commit -m "ci: run tests and package release build"
```

### Task 4: Add GitHub Release Publishing

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Add a release publication step that uploads the built executable to the tag release**

```yaml
      - name: Publish GitHub release asset
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.ref_name }}
          name: Text Delimiter Tool ${{ github.ref_name }}
          files: dist/TextDelimiterTool.exe
          generate_release_notes: true
```

- [ ] **Step 2: Review the completed workflow file for order and completeness**

Run: `powershell -Command "Get-Content '.github/workflows/release.yml'"`
Expected: checkout, Python setup, version validation, dependency install, tests, build, and release upload all appear in that order

- [ ] **Step 3: Commit the release upload step**

```bash
git add .github/workflows/release.yml
git commit -m "ci: publish tagged release assets"
```

### Task 5: Document The Automated Release Flow

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a short note in the release section describing the new tag-driven GitHub Actions flow**

```md
### GitHub Actions Release | GitHub Actions 自动发布

After implementation, pushing a tag such as `v1.0.1` will trigger GitHub Actions to validate the version, run tests, build `TextDelimiterTool.exe`, and upload it to the matching GitHub Release.

实现后，推送 `v1.0.1` 这类 tag 会自动触发 GitHub Actions 校验版本、运行测试、构建 `TextDelimiterTool.exe`，并上传到对应的 GitHub Release。
```

- [ ] **Step 2: Verify the README still contains the existing manual build instructions and now also mentions the automated release path**

Run: `powershell -Command "Get-Content 'README.md'"`
Expected: both the existing manual build section and the new GitHub Actions release note are present

- [ ] **Step 3: Commit the README release documentation update**

```bash
git add README.md
git commit -m "docs: document automated GitHub release flow"
```

### Task 6: End-To-End Verification

**Files:**
- Modify: `.github/workflows/release.yml`
- Modify: `README.md`

- [ ] **Step 1: Review the spec and verify each requirement maps to the implemented files**

Run: `powershell -Command "Get-Content 'docs/superpowers/specs/2026-03-31-github-actions-release-automation-design.md'"`
Expected: every item in scope is covered by `.github/workflows/release.yml` or `README.md`

- [ ] **Step 2: Run fresh local verification for the parts that can be tested locally**

Run: `powershell -Command "$env:PYTHONPATH='src'; python -m unittest tests.test_formatter -v"`
Expected: `OK`

Run: `powershell -Command "$env:PYTHONPATH='src'; python -m unittest tests.test_version -v"`
Expected: `OK`

Run: `powershell -Command "git diff -- .github/workflows/release.yml README.md"`
Expected: reviewable final diff with workflow and documentation changes only

- [ ] **Step 3: Push the branch changes and create a future test tag when ready**

```bash
git add .github/workflows/release.yml README.md
git commit -m "ci: automate tagged Windows releases"
git push origin main
```

- [ ] **Step 4: Trigger a real release workflow run with the next version tag after updating `VERSION`**

```bash
# Example future release flow
# 1. Edit VERSION to 1.0.1
# 2. Commit and push main
# 3. Create tag and push it

git tag v1.0.1
git push origin v1.0.1
```

Expected: GitHub Actions creates or updates the `v1.0.1` release and uploads `TextDelimiterTool.exe`
