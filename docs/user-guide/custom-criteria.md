# Custom Criteria Registration

mocaco is designed to be easily extensible by independent contributors. Adding a new convergence rule only requires creating a single module with a predefined structure and decorating a class with `@registry.register()`.

## The Criterion Protocol

To register a custom criterion, your class must satisfy the `Criterion` protocol. It requires:
1. **Parameters:** Defined as a Pydantic `BaseModel` for automatic validation.
2. **Metadata:** `name`, `description`, `assumptions`, `limitations`, `result_interpretation`, and `references`.
3. **Execution Logic:** A `run(self, samples, params)` method that computes the logic and returns a `ConvergenceResult`.

By placing your module in the `mocaco/methods/` directory, it is automatically discovered and accessible via the central API (e.g., `mcc.convergence.my_custom_rule()`), which allow any user using it in future mocaco releases. Alternativelly, you can also create it in your local project to use it easyly.

Note if you add a custom criterion locally some tools like Pylance will raise a notification such us:
```bash
Cannot access attribute "custom_criteria" for class "custom_criteria"
  Attribute "custom_criteria" is unknown
```

*See `examples/03_custom_criteria.py` for a runnable example.*
