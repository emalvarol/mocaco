# New planned tasks

## General (steps to reach 1.0.0 version)
- [ ] 1. Improve clt_uni_abs and associated to process columns:
    - assets or decide if create a new clt_uni_abs_assets
    - [ ] ADD warm-up TEST
    - [ ] ADD group_cols TEST
    - [ ] Check all test pass, ruf and mypy
- [ ] 2. Add basic criterions:
    - clt_uni_rlt, clt_multi_rlt (vats_2019)
- [ ] can/should I add future additions into changelog? Is changelos shown in pipy publication or in public documentation? Should it be there?
- [ ] launch release v.0.2.0


## GIT
Rama creada con: git checkout -b feature/user-guide-and-tutorials
luego usar para guardar rama en nuve: git push -u origin feature/user-guide-and-tutorials
luego para merge:
git checkout main
git pull origin main
git merge feature/user-guide-and-tutorials
git push origin main
