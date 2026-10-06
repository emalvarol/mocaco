# New planned tasks
NOTE: Each task is marked in the code with a comment with exclamation "#!"
and the respective code. For example: #! a1.
Sometimes with a note, for instance: #! a1. Include None to allow...

## General (steps to reach 1.0.0 version)
- [x] 1. ruff configuration
- [x] 2. Type checking strict configuration
- [x] 3. input valitadion and edge case handling (NaN, Inf, Null). Update SampleFrame
- [x] 4. Add a rich summary for results. Update ConvergenceResults
- [ ] 5. Basic plotting capabilities and export hooks (to_pandas, to_polars)
- [ ] 6. Comprehensive test coverage
- [ ] 7. Automate test workflow in GitHub Actions (ci.yml) across python versions (3.9, 3.10, 3.11 y 3.12) and every pull request and push to main
- [ ] 8. Add basic criterions:
    - clt_relative, std_error, relative_change
- [ ] 9. User Guide & Tutorials providing worked examples covering noise vs smooth convergence custom criterion registration via wrapper and Polars integration patters
- [ ] 10. CONTRIBUTING.md Guidelines for external developers registering new convergence criteria.
- [ ] 11. Project Files CHANGELOG.md Document release notes for 1.0.0
- [ ] 12. PyPI Publish workflow (publish.yml) (uv build / build)