# Computerdesignment-contest

For our computerdesignment-contest.

---
## 采用本地命令行进行操作，单次具体流程如下：

1. `git switch -c branch-name`（这个是自己设置的，可以用中文，用feature/开头）  #创建新的分支
2. **新建文件保存** #建立一个新的单独的文件储存自己部分的功能
3. `git add .`  #暂存提交，还未提交远端和本地
4. `git commit -m "注释"` (说明提交的功能是干嘛的） #提交到本地仓库，注释是本次提交的说明
5. 如果准备提交分支，在此处进行检查main是否最新，检查完毕后切换回对应的分支
6. `git push origin “你刚刚创建的分支名字”`  #提交到远端仓库 必须切换到对应的分支提交！！
7. 此时 GitHub 上边应该有 PR 请求，回到网页勾选 reviewer 的人，必须确定无误后才能同意 PR 请求并 merge #每次必须从最新的 main 分支提交上去（重点!)

---

## 如何检查本地 main 是否是最新

1. `git branch`  #查看当前所处的分支
2. 如果出现 `* main`，则处于 main 分支，否则执行第三步
3. `git checkout main`  #切换到 main 分支
4. `git fetch origin`  #云端的更新信息“拉”到本地
5. `git status`  #对比是否最新，如果不是最新，执行第六步
6. `git pull origin main`  #拉取，将本地 main 分支更新到最新
7. `git checkout branch-name`  #切换回自己新建的分支,所有操作在新建的分支操作！

---

## 每次准备开发前的准备

1. 检查 main 分支是否最新
2. 不是则更新
3. 更新后切换回去

> **注意：** 所有的功能分支合并到 main 分支操作都要在网页端操作，并且需要其他人审核
