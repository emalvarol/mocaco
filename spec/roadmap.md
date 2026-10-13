# New planned tasks

## General (steps to reach 1.0.0 version)
- [ ] 1. Improve clt_uni_abs and associated to process columns:
    - assets or decide if create a new clt_uni_abs_assets: we may handle it by using the properties of grouped results
- [ ] can/should I add future additions into changelog? Is changelos shown in pipy publication or in public documentation? Should it be there?
- [ ] launch release v.0.2.0
- [ ] 2. Add basic criterions:
    - clt_uni_rlt, clt_multi_rlt (vats_2019)
- [ ] launch release v.0.3.0

## Test
- [ ] Use conftest dataframe for tests/methods/test_clt_uni_abs.py::test_clt_run_zero_variance
- [ ] Add test analogous to ConvergenceResult for GroupedConvergenceResult
- [ ] ADD warm-up TEST
- [ ] ADD group_cols TEST

## GIT
Rama creada con: git checkout -b feature/user-guide-and-tutorials
luego usar para guardar rama en nuve: git push -u origin feature/user-guide-and-tutorials
luego para merge:
git checkout main
git pull origin main
git merge feature/user-guide-and-tutorials
git push origin main
