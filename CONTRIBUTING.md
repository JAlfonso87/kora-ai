# Contributing to Kora AI

This document defines the development and collaboration conventions for the Kora AI project.

## 1\. General Guidelines

* Technical names must be written in English.
* Keep code organized into small, cohesive modules with clearly defined responsibilities.
* Avoid unnecessary duplication and keep implementations as simple as possible.
* Changes should be related to the User Story being implemented.
* Do not introduce technologies, dependencies, or architectural changes without prior agreement from the team.

## 2\. Naming Conventions

Technical names must use English and follow the conventions of the language or technology being used.

### Python

|Element|Convention|Example|
|-|-|-|
|Variables|`snake\_case`|`user\_context`|
|Functions|`snake\_case`|`get\_user\_context()`|
|Classes|`PascalCase`|`UserContext`|
|Constants|`UPPER\_SNAKE\_CASE`|`MAX\_RETRIES`|
|Files|`snake\_case`|`user\_service.py`|
|Directories|`snake\_case`|`agent\_service/`|

### General Technical Elements

* API endpoints should use clear, consistent, and resource-oriented names.
* Environment variables must use `UPPER\_SNAKE\_CASE`.
* Models, schemas, services, and other technical components must use descriptive names that clearly represent their responsibility.
* Avoid ambiguous abbreviations and names that do not communicate the purpose of the element.

Technology-specific conventions may be defined when the corresponding technology is introduced into the project.

## 3\. Branches

Branches must follow the format:

```text
type/HU-XXX
```

The following branch types are defined:

|Type|Purpose|Example|
|-|-|-|
|`feature`|New functionality or User Story implementation|`feature/HU-003`|
|`fix`|Bug correction|`fix/HU-003`|
|`docs`|Documentation changes|`docs/HU-001`|
|`refactor`|Code restructuring without changing functionality|`refactor/HU-003`|
|`test`|Adding or modifying tests|`test/HU-003`|

For the implementation of a User Story, `feature/HU-XXX` should be the standard branch type.

The other branch types should be used only when the corresponding change requires an independent branch.

Examples:

```text
feature/HU-003
fix/HU-003
docs/HU-001
refactor/HU-003
test/HU-003
```

The `main` branch must contain integrated and reviewed changes only.

## 4\. Commits

Commits must reference the User Story they belong to.

Format:

```text
type(HU-XXX): description
```

Allowed commit types:

* `feat` — New functionality
* `fix` — Bug correction
* `docs` — Documentation changes
* `test` — Tests
* `refactor` — Code restructuring without changing functionality

Examples:

```text
feat(HU-003): add agent endpoint
fix(HU-003): handle invalid request
test(HU-003): add agent endpoint tests
docs(HU-003): update API documentation
```

Commits should be clear and describe the change they introduce.

A User Story may contain multiple commits while it is being developed.

## 5\. Pull Requests

When a User Story is ready for integration, the developer must create a Pull Request from the corresponding feature branch into `main`.

Pull Requests must:

* Clearly indicate the User Story being implemented.
* Describe the changes made.
* Include relevant tests or validation performed.
* Meet the acceptance criteria of the User Story.
* Be reviewed by at least one other team member.

The author of a Pull Request cannot approve or merge their own Pull Request.

## 6\. Code Review

Reviewers should verify:

* The implementation follows the project's conventions.
* The changes correspond to the User Story.
* The code is understandable and appropriately modular.
* No unnecessary changes or dependencies were introduced.
* Tests and acceptance criteria are adequately covered.

Any relevant issue should be addressed before the Pull Request is merged.

## 7\. Integration Process

The standard development workflow is:

```text
User Story
    ↓
Create feature/HU-XXX
    ↓
Develop and commit changes
    ↓
Run tests and validations
    ↓
Create Pull Request
    ↓
Code Review
    ↓
Approval
    ↓
Merge into main
```

After merging, the feature branch may be deleted if it is no longer needed.

## 8\. Documentation

Documentation should be updated when a change affects:

* Project setup
* Development workflow
* Architecture
* APIs
* Configuration
* Development conventions

Documentation must use English for technical content and follow the structure established by the project.

