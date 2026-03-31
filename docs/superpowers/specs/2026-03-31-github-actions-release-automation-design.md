# GitHub Actions Release Automation Design

Date: 2026-03-31

## Goal

Add a GitHub Actions workflow that automatically validates, builds, and publishes the Windows executable when a version tag such as `v1.0.1` is pushed.

目标是增加一个 GitHub Actions 工作流：当推送 `v1.0.1` 这类版本 tag 时，自动执行校验、打包，并发布 Windows 可执行文件。

## Scope

Included:

- Trigger on pushed Git tags matching `v*`
- Run on GitHub-hosted Windows runners
- Install Python and packaging dependency
- Run formatter and version tests before release
- Build `dist/TextDelimiterTool.exe` using the existing `scripts/build.ps1`
- Create or update the matching GitHub Release
- Upload the packaged `.exe` as a release asset
- Fail fast when tag version and `VERSION` file do not match

包含：

- 监听 `v*` 格式的 Git tag 推送
- 在 GitHub 托管的 Windows runner 上运行
- 安装 Python 和打包依赖
- 发布前执行 formatter 和 version 测试
- 复用现有 `scripts/build.ps1` 构建 `dist/TextDelimiterTool.exe`
- 创建或更新对应的 GitHub Release
- 上传打包后的 `.exe` 作为 Release 附件
- 当 tag 版本与 `VERSION` 文件不一致时快速失败

Excluded:

- Automatic publishing on every push to `main`
- Multi-platform builds
- Automatic changelog generation
- MSI or installer packaging
- Signing the executable

不包含：

- 每次推送到 `main` 都自动发布
- 多平台构建
- 自动生成 changelog
- MSI 或安装器打包
- 可执行文件签名

## Recommended Approach

Use a single workflow file at `.github/workflows/release.yml` triggered by tag pushes. The workflow should remain small and reuse the repository's existing packaging script rather than duplicating PyInstaller logic in YAML.

推荐使用单个 `.github/workflows/release.yml` 工作流，通过 tag push 触发。工作流本身保持轻量，尽量复用仓库现有的打包脚本，而不是在 YAML 里重复写一遍 PyInstaller 逻辑。

Why this approach:

- Matches the current manual release process already in use
- Keeps versioning centered on the existing `VERSION` file and release tag
- Minimizes future maintenance by reusing `scripts/build.ps1`
- Makes a release an explicit act, not an accidental side effect of routine commits

原因：

- 与当前已经在使用的手工 Release 流程一致
- 继续以现有 `VERSION` 文件和 Git tag 作为版本来源
- 复用 `scripts/build.ps1`，后续维护成本更低
- Release 是显式发布动作，而不是普通提交的副作用

## Alternatives Considered

### Option 1: Tag-triggered release workflow

Recommended.

Pros:

- Clear release boundary
- Easy to reason about versioning
- Lowest chance of accidental public releases

Cons:

- Requires creating and pushing a tag for each release

### Option 2: Build on `main`, release on tags

Pros:

- Continuous validation on everyday pushes
- Release path still stays explicit

Cons:

- More workflow complexity than needed right now
- Adds CI surface area before the project actually needs it

### Option 3: Manual workflow dispatch

Pros:

- Maximum control from GitHub UI

Cons:

- Keeps part of the release flow manual
- Easier to forget version alignment steps

## Workflow Design

### Trigger

The workflow triggers on:

```yaml
on:
  push:
    tags:
      - 'v*'
```

This ensures release automation only runs for version tags.

### Runner

Use `windows-latest` because the output artifact is a Windows executable and the current packaging script is PowerShell-based.

### Steps

1. Check out the repository.
2. Set up Python 3.13.
3. Install `pyinstaller`.
4. Read `VERSION` and compare it to the pushed tag without the leading `v`.
5. Export `PYTHONPATH=src` for test execution.
6. Run `tests.test_formatter`.
7. Run `tests.test_version`.
8. Execute `powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Clean`.
9. Create or update the GitHub Release for the tag.
10. Upload `dist/TextDelimiterTool.exe` as the release asset.

### Version Consistency Rule

The workflow must enforce:

- Tag `v1.0.1` matches `VERSION` content `1.0.1`

If they do not match, the workflow stops before any release is created.

这条约束必须被强制执行：

- tag `v1.0.1` 必须对应 `VERSION` 文件中的 `1.0.1`

如果不一致，工作流在创建 Release 前直接失败。

### Release Content

The workflow should:

- Reuse the tag as the release tag
- Use a simple title such as `Text Delimiter Tool v1.0.1`
- Upload `TextDelimiterTool.exe`
- Avoid embedding large generated release notes logic in the first version

### Authentication

Use the repository-provided `GITHUB_TOKEN` to create the release and upload assets. No personal token should be required.

## Error Handling

Expected failure modes and responses:

- `VERSION` missing: fail immediately
- Tag format invalid: fail immediately
- Tag/version mismatch: fail immediately
- Unit tests fail: fail before build
- Build script fails: fail before release upload
- Asset upload fails: workflow fails, leaving logs for retry diagnosis

## Testing Strategy

Validation should happen at three levels:

1. Local script validation: ensure `scripts/build.ps1` still builds successfully.
2. Workflow dry validation by reviewing YAML structure and command syntax.
3. Real integration test by creating a future release tag such as `v1.0.1` after implementation.

## Files To Add Or Update

Add:

- `.github/workflows/release.yml`

Update if needed:

- `README.md` to document the new automated release flow

## Operational Flow After Implementation

Future release process should become:

1. Update `VERSION`
2. Commit and push to `main`
3. Create and push tag `vX.Y.Z`
4. GitHub Actions builds and publishes the executable automatically

实施后，未来发布流程应变成：

1. 修改 `VERSION`
2. 提交并推送到 `main`
3. 创建并推送 `vX.Y.Z` tag
4. GitHub Actions 自动构建并发布可执行文件

## Risks And Mitigations

- Risk: Windows runner behavior differs slightly from local machine
  Mitigation: keep the workflow dependent on the same PowerShell build script already verified locally

- Risk: release asset name changes unexpectedly
  Mitigation: upload the explicit path `dist/TextDelimiterTool.exe`

- Risk: version drift between tag and file
  Mitigation: add a dedicated consistency check step before tests and build

## Success Criteria

The design is successful when:

- Pushing `vX.Y.Z` triggers the workflow automatically
- The workflow fails on mismatched versions
- The workflow passes on valid tagged releases
- A GitHub Release is created or updated for that tag
- `TextDelimiterTool.exe` is attached to the release without manual upload
