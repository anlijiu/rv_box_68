# 代理规则

## 通用规则
- 默认使用中文沟通、分析和提交说明。
- 该项目使用uv来管理其环境。
- 必须立即更正过时/不正确的文档（包括此文件）。
- 所有 Python 文件顶部都必须有注释，说明该文件的功能，格式为：文件功能：[此处填写功能说明]。文件更改时，注释也应及时更新。
- 所有 Python 模块都__init__.py必须在顶部添加注释，解释整个模块的职责，格式如下：模块职责：[此处填写职责]
- 如果要求你复制或移动文件，最好使用 cp 或 mv 命令。
- 当被要求更新或修复文档或任何 Markdown 文件时，不要以任何方式表明内容已经更改。例如，不要写“更新：我们现在想做 X”。要以自然流畅的方式编写，就像是最初的版本一样。 
- 不要写提及已修复的错误的评论（除非明确要求），因为此类评论从长远来看毫无用处。
- 仅在被要求时才执行 git commit。提交信息请使用常规提交格式。
- 未经用户批准，绝对不允许从 git 检出文件。
- 禁止使用任何不规范的补丁。如果感觉需要大量工作才能干净利落地实现某个功能（不使用补丁），请停止操作并向用户寻求指导。力求编写 100% 简洁、易读、易维护的代码。
    + 同样，除非用户明确批准，否则任何地方都不允许使用向后兼容代码。
- 除非此代码库中存在已确认的合法调用者/用例，否则不要实现回退路径、防御性兼容性垫片或备用代码路径；如果不存在，则删除或拒绝回退。
- 如果代码达到不可能的状态，RuntimeError立即抛出异常（或更具体的异常）。不要返回None默认值，也不要静默继续执行。
- 在类型和函数签名中编码不变式：如果None无效，则不要使用可选返回类型。在入口点验证前提条件，然后保持内部辅助函数严格且非可选。
- 重构时不要删除有用的行注释。
- 请务必为所有公共函数/方法添加注释，并在私有/内部方法的名称不足以充分描述其逻辑时也添加注释。
- 当语义不够清晰时，请对 if 语句和其他代码路径决策添加注释。
- 用空行隔开代码注释和前面的代码，使代码注释前面有一个空行。

## 测试理念
只编写有意义的、长期的测试。避免编写毫无意义的“愚蠢测试”：

**DO NOT write:**
- Tests checking for non-existence of fields/classes (negative tests) - these will never fail unless architecture fundamentally changes
- Phase-specific test files (e.g., `test_*_phase2.py`) - clean up TDD artifacts after implementation
- Tests that duplicate existing coverage without adding value
- Tests for implementation details that may change during refactoring
- Tests of fake internals, protocol compliance, or method existence - fakes support tests, they are not product behavior
- Private attribute assertions (`_git_port`, `_git_service`, `hasattr` checks) - these freeze wiring details
- Dataclass default/repr/mutability trivia unless it documents a public contract
- Permanently skipped or debug-only tests

**DO write:**
- Positive tests verifying components ARE wired correctly through observable outcomes
- Tests for behavioral contracts and public APIs
- Integration tests validating component interactions that require real FreeCAD/Qt runtime
- Tests that would catch regressions if removed

**Layer ownership:** Each behavior has one owning test layer. Domain owns algorithms. Application owns orchestration and result contracts. Infrastructure owns adapter parsing and error mapping. UI owns observable presenter/view behavior. Integration owns real FreeCAD/Qt/runtime behavior. Do not duplicate tests across layers.

**Skipped tests:** Never leave skipped tests in the suite long-term. Move useful runtime-dependent coverage to integration tests; delete the rest.

**Parametrized consolidation:** Use `@pytest.mark.parametrize` when multiple tests differ only in input/output values. Keeps edge coverage concise and reduces repetitive failures.

**Mocking stdlib modules:** Use `unittest.mock.patch` context managers instead of `monkeypatch.setattr` when patching standard library modules (`subprocess`, `os`, `pathlib`). This prevents global state from leaking into IDE pytest hooks. `monkeypatch` is fine for application-specific modules.

**Path safety for tests:** Do not use `/tmp` or `/var/tmp` paths in tests. Use stable fake paths such as `/home/user/dir/...` to avoid FreeCAD Addons Report static analyzer for insecure-temp-path findings.


