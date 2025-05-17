# Linter Progressive Enforcement Plan

This document tracks the plan for progressively enabling and enforcing all Ruff and Pylint rules in the codebase. The goal is to reach full compliance by addressing one rule at a time, starting with the highest-priority or easiest-to-fix issues.

## Current Disabled Rules

### Ruff
- E203: Whitespace before ':' (ignored for Black compatibility)
- E501: Line too long (handled by Black)
- D203: 1 blank line required before class docstring (prefer D211)
- D213: Multi-line docstring summary should start at the second line (prefer D212)
- D100, D101, D102, D103, D107, D205, D212: Docstring style (missing or formatting issues)
- PLR2004: Magic value used in comparison
- PLR0913: Too many arguments in function definition
- PLR0917: Too many positional arguments
- PLR0912: Too many branches
- PLR0915: Too many statements
- PLR0902: Too many instance attributes
- PLR0903: Too few public methods
- PLR0904: Too many public methods
- W1203: Use lazy % formatting in logging functions
- W0718: Catching too general exception Exception
- W0511: TODO/fixme in code
- C408: Unnecessary dict() call
- E1136: Value unsubscriptable
- W0212: Access to a protected member
- W0613: Unused argument
- W0105: Pointless string statement
- R0801: Duplicate code
- W1514: open() without encoding
- Per-file ignore: F401 (unused import) in __init__.py

### Pylint
- C0301: Line too long (handled by Black)
- R0902: Too many instance attributes
- R0913: Too many arguments
- R0917: Too many positional arguments
- R0912: Too many branches
- R0915: Too many statements
- R0903: Too few public methods
- R0904: Too many public methods
- W1203: Use lazy % formatting in logging functions
- W0718: Catching too general exception Exception
- W0511: TODO/fixme in code
- C408: Unnecessary dict() call
- E1136: Value unsubscriptable
- W0212: Access to a protected member
- W0613: Unused argument
- W0105: Pointless string statement
- R0801: Duplicate code
- W1514: open() without encoding

## Rule Descriptions and Fix Priority

| Rule         | Description                                              | Priority | Notes/Plan |
|--------------|---------------------------------------------------------|----------|------------|
| D1xx/D2xx    | Docstring style and presence                            | High     | Add/fix docstrings, enforce PEP 257 |
| PLR2004      | Magic value in comparison                               | High     | Refactor to named constants         |
| PLR0913/17   | Too many arguments/positional arguments                 | Med      | Refactor signatures                 |
| PLR0912/15   | Too many branches/statements                            | Med      | Refactor complex functions          |
| PLR0902/3/4  | Too many/few instance/public methods                    | Low      | Refactor classes                    |
| W1203        | Logging f-string interpolation                          | High     | Use lazy % formatting               |
| W0718        | Catching too general exception                          | High     | Catch more specific exceptions      |
| W0511        | TODO/fixme in code                                      | Low      | Address TODOs as time allows        |
| C408         | Unnecessary dict() call                                 | Low      | Use dict literals                   |
| E1136        | Value unsubscriptable                                   | High     | Fix type issues                     |
| W0212        | Access to protected member                              | Med      | Refactor to avoid                   |
| W0613        | Unused argument                                         | Low      | Remove or use arguments             |
| W0105        | Pointless string statement                              | Low      | Remove stray strings                |
| R0801        | Duplicate code                                          | Med      | Refactor to remove duplication      |
| W1514        | open() without encoding                                 | High     | Specify encoding                    |

## Next Steps

1. Suppress all above rules in Ruff and Pylint config so linters pass.
2. Tackle one rule at a time: Remove from ignore/disable, fix codebase, and update this plan.
3. Update this document and TODO.md as progress is made. 