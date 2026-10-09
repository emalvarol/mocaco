# New planned tasks

## General (steps to reach 1.0.0 version)
- [x] 1. Update main spec with current codebase
- [x] 2. Remove supports_eval_frequency from protocol and existing method since the wrapper was deprecated and removed
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
