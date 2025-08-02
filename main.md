# vibe coding工作流

## 一，git

#### 1.git工作流策略-GitFlow工作流

1.  **main (或 master) 分支:**

    *   **用途:** 永远代表了**可部署的、稳定的生产版本**。
    *   **规则:** 绝对禁止直接向 main 分支提交代码。所有代码都必须从其他分支合并（Merge）进来。main 分支上的每一个 commit 都应该对应一个发布的版本，并且都应该打上一个标签（Tag），例如 v1.0.0, v1.1.0。
    *   **部署:** 您的**部署版本就应该是 main 分支上最新的、打了标签的那个 commit**。
2.  **develop 分支:**

    *   **用途:** 这是**功能集成的开发主分支**。所有新功能开发完成後，都合并到这个分支。它代表了下一个版本将要发布的所有功能。
    *   **规则:** 这是一个相对不稳定的分支，但它应该是功能完整的。
3.  **feature/\* (例如 feature/user-login) 分支:**

    *   **用途:** 开发新功能。每个新功能都应该从 develop 分支切出来。
    *   **规则:** 功能开发完成后，合并回 develop 分支，然后删除该 feature 分支。
4.  **release/\* (例如 release/v1.1.0) 分支:**

    *   **用途:** 当 develop 分支上的功能积累到可以发布一个新版本时，从 develop 分支切出一个 release 分支。
    *   **规则:** 在这个分支上，**不再开发新功能**。只进行版本发布前的最后测试、Bug修复、文档生成、版本号更新等准备工作。
    *   **完成发布:** 当 release 分支准备就绪后，它必须被同时合并到 main 分支（用于发布）和 develop 分支（确保 develop 也包含了这些Bug修复）。合并到 main 后，打上版本标签（Tag）。
5.  **hotfix/\* (例如 hotfix/bug-in-v1.0.1) 分支:**

    *   **用途:** 修复线上（main 分支）出现的紧急Bug。
    *   **规则:** 直接从 main 分支切出。修复完成后，同时合并回 main 和 develop 分支。

#### 2,git多分支本地开发方案

核心思想：一人分饰两角或多角，并行开发

利用 AI 编码或编译的等待时间，在同一台电脑上同时处理两个或多个不同功能的开发任务，最大化个人生产力。

##### **推荐方案：`git worktree` + `reb`**`ase`

##### 1.2.1搭建并行环境 (`git worktree`)

1.  **首次克隆**: 只需克隆一次项目作为“主工作区”。
    ```bash
    git clone <repo_url> my-project
    cd my-project
    ```
2.  **创建功能A工作区**: 在主工作区内创建 `feature-A` 分支并开始工作。
    ```bash
    git checkout -b feature-A
    ```
3.  **创建功能B工作区**: 使用 `worktree` 命令，从主分支 (`main`) 创建一个全新的、隔离的工作文件夹 `my-project-feature-B`，并自动检出新分支 `feature-B`。
    ```bash
    git worktree add ../my-project-feature-B -b feature-B main
    ```
4.  **开始工作**:
    *   用编辑器打开 `my-project` 文件夹，专心开发 `feature-A`。
    *   同时用另一个编辑器窗口打开 `my-project-feature-B` 文件夹，专心开发 `feature-B`。
    *   两者互不干扰，但共享同一个底层的 Git 数据库。

##### 1.2.2日常开发与同步 (`rebase`)

1.  **保持同步**: 为了避免与主分支（`main`）脱节太远，养成**每天开始工作时**同步最新代码的习惯。
2.  **同步步骤**: 在你的功能分支（如 `feature-A`）下执行：
    ```bash
    # 0. (若有未提交的修改) 先 commit 或 stash
    git commit -am "WIP"  # 或者 git stash

    # 1. 获取远程最新信息
    git fetch origin

    # 2. 将你的分支“变基”到最新的 main 分支上
    git rebase origin/main
    ```
3.  **处理冲突**: 如果 `rebase` 过程中提示冲突：
    a.  打开冲突文件，手动编辑，保留所有需要的代码，并删除 `<<< === >>>` 标记。
    b.  `git add <冲突文件>`
    c.  `git rebase --continue`
    d.  重复直至 `rebase` 完成。

##### 1.2.3功能完成与清理

1.  **合并**: 功能完成后，通过 Pull Request 将你的功能分支（如 `feature-A`）合并到 `main`。
2.  **清理分支**: 合并后，删除远程和本地的功能分支。
    ```bash
    git push origin --delete feature-A
    git branch -d feature-A
    ```
3.  **清理工作区**: 使用 `worktree remove` 命令安全地移除对应的物理文件夹和 Git 记录。
    ```bash
    git worktree remove ../my-project-feature-A
    ```

# 2，开发模型

#### 1，敏捷开发模型（变体）

**Phase 0: 奠基阶段 (Foundation)**

1.  **编写“活”的PRD (Living PRD)**

    *   专注于核心功能 (MVP)。不用一次性写完所有细节。这份PRD会随着你的思考和AI的反馈而演进。
    *   **关键**：用清晰、结构化的语言，最好带有明确的“验收标准”，这是给AI最好的养料。

**Phase 1: 规划阶段 (Planning)**\
2. **使用xitools工具分解PRD到任务看板 (e.g., Trello, Notion, Jira)**\
\* 将PRD中的一个功能模块（如“用户系统”）拆解成一个个具体的任务卡片（“开发注册接口”、“开发登录接口”、“设计数据库表结构”等）。\
\* 按优先级排序。

**Phase 2: 开发-测试循环 (The Core Loop - Per Task)**\
*这是一个针对看板上**每一张**任务卡的循环*

1.  **选择一个任务卡，并精心设计“超级指令 (Super-Prompt)”**

    *   指令中包含：

        *   任务目标（来自任务卡）。
        *   相关PRD片段。
        *   相关的上下文（如数据库表结构、已有的代码规范）。
        *   **明确的测试要求（如上所述）**。
2.  **生成产出物**

    *   生成代码（如 user.controller.js）。
    *   生成单元测试代码（如 user.controller.test.js）。
    *   生成相关文档草稿（如API文档片段）。
3.  **审查、测试、集成 (The Human-in-the-Loop - 关键反馈环)**

    *   **代码审查**：代码逻辑是否正确、安全？
    *   **运行单元测试**：npm test，查看所有测试是否通过。
    *   **手动API测试**：在Postman中调用接口，进行探索性测试。
    *   **发现问题？** -> 回到第3步，提出更具体的修改指令（例如：“你在上个版本中没有校验密码复杂度，请加上，并更新测试用例”）。
    *   **没有问题？** -> 将AI生成的代码和测试合并到你的主代码库中。
4.  **完成并归档文档**

    *   你将AI生成的、已经过验证的文档片段，整理到专门的文档文件夹中（如使用Obsidian, Notion管理）。AI可以帮你格式化，但最终由你来归档确认。
5.  **将任务卡移动到“Done”列**，然后回到第3步，处理下一个任务。

**Phase 3: 整体集成与发布 (Integration & Release)**\
8. **进行端到端测试 (E2E Testing)**\
\* 当一个完整的功能模块（如整个用户系统）的所有任务都完成后，进行贯穿整个流程的测试。\
9. **部署**\
\* 可以请求AI为你编写部署脚本（如Dockerfile、CI/CD配置文件），但最终部署由你操作和验证。
