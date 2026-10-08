# New planned tasks

## General (steps to reach 1.0.0 version)
- [ ] remove wrapper
- [ ] 13. Add basic criterions:
    - clt_uni_rlt, clt_multi_rlt (vats_2019)

## Minor improvements
- [ ] Make pandas, matplotlib optionals dependencies
- [ ] standarize n using it instead
- [ ] standarize stimate using metric instead
- [ ] update test_spec with the implemented test
- [ ] update github actions to run stub and docs script with every pull (is that possible?)

## GIT
Rama creada con: git checkout -b feature/user-guide-and-tutorials
luego usar para guardar rama en nuve: git push -u origin feature/user-guide-and-tutorials
luego para merge:
git checkout main
git pull origin main
git merge feature/user-guide-and-tutorials
git push origin main
