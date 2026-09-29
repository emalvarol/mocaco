# New planned tasks
NOTE: Each task is marked in the code with a comment with exclamation "#!"
and the respective code. For example: #! a1.
Sometimes with a note, for instance: #! a1. Include None to allow...

## General (steps to reach 1.0.0 version)

- [ ] Add basic criterions:
    - clt_relative, std_error, relative_change
- [ ] input valitadion and edge case handling (NaN, Inf, Null)
- [ ] Graceful handling when $n < \text{stb\_window}$ or $n < 2$ (sample variance underflow).
- [ ] Basic plotting capabilities and export hooks (to_pandas, to_polars)
- [ ] Add a rich summary for results
- [ ] Comprehensive test coverage
- [ ] Type checking strict configuration
- [ ] ruff configuration
- [ ] Automate test workflow in GitHub Actions (ci.yml) across python versions and every pull request and push to main
- [ ] PyPI Publish workflow (publish.yml) (uv build / build)
- [ ] User Guide & Tutorials providing worked examples covering noise vs smooth convergence custom criterion registration via wrapper and Polars integration patters
- [ ] Project Files CHANGELOG.md Document release notes for 1.0.0
- [ ] CONTRIBUTING.md Guidelines for external developers registering new convergence criteria.
