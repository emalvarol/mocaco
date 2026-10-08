# New planned tasks

## General (steps to reach 1.0.0 version)
- [x] 1. ruff configuration
- [x] 2. Type checking strict configuration
- [x] 3. input valitadion and edge case handling (NaN, Inf, Null). Update SampleFrame
- [x] 4. Add a rich summary for results. Update ConvergenceResults
- [x] 5. Basic plotting capabilities and export hooks (to_pandas, to_polars)
- [x] 6. Comprehensive test coverage
- [x] 7. Automate test workflow in GitHub Actions (ci.yml) across python versions (3.12, 3.13, 3.14) and every pull request and push to main
- [x] 8. CONTRIBUTING.md Guidelines for external developers registering new convergence criteria.
- [x] 9. Project Files CHANGELOG.md Document release notes for 1.0.0
- [x] 10. PyPI Publish workflow (publish.yml) (uv build / build)
- [ ] 11. User Guide & Tutorials providing worked examples covering noise vs smooth convergence custom criterion registration via wrapper and Polars integration patters
- [ ] 12. Add basic criterions:
    - clt_uni_rlt, clt_multi_rlt (vats_2019)

## Minor improvements
- [ ] Make pandas, matplotlib optionals dependencies
- [ ] standarize n using it instead
- [ ] standarize stimate using metric instead
- [ ] change clt_absolute to clt_uni_abs
- [ ] update test_spec with the implemented test
- [ ] update github actions to run stub and docs script with every pull (is that possible?)
- [ ] update changelog for realease 1.0.0
- [ ] improve documentation for github, where do I see the docs? Wiki, independent web?


## GIT
Rama creada con: git checkout -b feature/user-guide-and-tutorials
luego usar para guardar rama en nuve: git push -u origin feature/user-guide-and-tutorials
luego para merge:
git checkout main
git pull origin main
git merge feature/user-guide-and-tutorials
git push origin main
