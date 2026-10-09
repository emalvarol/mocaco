# New planned tasks

## General (steps to reach 1.0.0 version)
- [ ] 1. Fix documentation, do not found or do not update automatically existing method agains old. clt_absolute was removed, now I have clt_uni_abs. clt_absolute is actualy in docs and a not found error appear in docs but witouth any warning nor error during docs generations. Fix generate_docs.py. README copy do not working, first page is still not that.
- [ ] 2. Update main spec with current codebase
- [ ] 3. Add basic criterions:
    - clt_uni_rlt, clt_multi_rlt (vats_2019)


## GIT
Rama creada con: git checkout -b feature/user-guide-and-tutorials
luego usar para guardar rama en nuve: git push -u origin feature/user-guide-and-tutorials
luego para merge:
git checkout main
git pull origin main
git merge feature/user-guide-and-tutorials
git push origin main
