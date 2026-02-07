# Computerdesignment-contest
For our computerdesignment-contest.
采用本地命令行进行操作，单次具体流程如下：
1.git switch -c branch-name（这个是自己设置的，可以用中文，用feature/开头）      #创建新的分支
2.新建文件保存                                                                #建立一个新的单独的文件储存自己部分的功能
3.git add .                                                                  #暂存提交，还未提交远端和本地
4.git commit -m "注释"(说明提交的功能是干嘛的）                                 #提交到本地仓库，注释是本次提交的说明
5.git push origin “你刚刚创建的分支名字”                                       #提交到远端仓库
6.此时GitHub上边应该有PR请求，回到网页勾选reviewer的人，必须确定无误后才能同意PR请求并merge   #每次必须从最新的main分支提交上去（重点!)

如何检查本地main是否是最新
1.git branch                                   #查看当前所处的分支
2.如果出现* main，则处于main分支，否则执行第三步
3.git checkout main                             #切换到main分支
4.git status                                    #对比是否最新，如果不是最新，执行第五步
5.git pull origin main                          #拉取，将本地main分支更新到最新

每次准备开发前的准备
1。检查main分支是否最新
2.不是则更新

注意：所有的功能分支合并到main分支操作都要在网页端操作，并且需要其他人审核
