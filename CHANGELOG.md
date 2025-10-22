# [1.3.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.2.1...v1.3.0) (2025-10-22)


### Features

* add ascent report command ([#5](https://github.com/dreamiurg/peakbagger-cli/issues/5)) ([3e6b2bf](https://github.com/dreamiurg/peakbagger-cli/commit/3e6b2bf29d3f8464b9390e699689b5c219282e3c))

## [1.2.1](https://github.com/dreamiurg/peakbagger-cli/compare/v1.2.0...v1.2.1) (2025-10-22)


### Bug Fixes

* handle varying table structures in peak ascents parser ([#6](https://github.com/dreamiurg/peakbagger-cli/issues/6)) ([c0639f3](https://github.com/dreamiurg/peakbagger-cli/commit/c0639f337617fec9644d9ac14008b84384c0e75e))

# [1.2.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.1.0...v1.2.0) (2025-10-21)


### Features

* require tests to pass before creating release ([#4](https://github.com/dreamiurg/peakbagger-cli/issues/4)) ([3aa984d](https://github.com/dreamiurg/peakbagger-cli/commit/3aa984df1aa53c5dd9c76fd7ce8f304d53513ddd))

# [1.1.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.0.0...v1.1.0) (2025-10-21)


### Bug Fixes

* configure semantic-release to use deploy key for pushing ([#3](https://github.com/dreamiurg/peakbagger-cli/issues/3)) ([915453b](https://github.com/dreamiurg/peakbagger-cli/commit/915453b75856a7ec52f70a6c00b5a7fa4b19819d))


### Features

* add VCR-based smoke tests for CLI commands ([#2](https://github.com/dreamiurg/peakbagger-cli/issues/2)) ([b5ffc62](https://github.com/dreamiurg/peakbagger-cli/commit/b5ffc62f2b3dbcca39f5b6ff5a990b948d7d1127))

# [1.0.0](https://github.com/dreamiurg/peakbagger-cli/compare/v0.6.2...v1.0.0) (2025-10-21)


* feat!: restructure CLI to resource-action pattern ([caa911e](https://github.com/dreamiurg/peakbagger-cli/commit/caa911e0688fb3bd82c1da53b6967608c93eb4e3))


### BREAKING CHANGES

* All command names have changed to use resource-action
pattern. Users must update scripts and workflows to use new command
structure (e.g., 'peakbagger peak search' instead of 'peakbagger search').

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

## [0.6.2](https://github.com/dreamiurg/peakbagger-cli/compare/v0.6.1...v0.6.2) (2025-10-21)


### Bug Fixes

* ensure consistent non-underlined blue URL formatting ([11a3c09](https://github.com/dreamiurg/peakbagger-cli/commit/11a3c0940da8b37533cfb3326686227e97abdf6a))

## [0.6.1](https://github.com/dreamiurg/peakbagger-cli/compare/v0.6.0...v0.6.1) (2025-10-21)


### Bug Fixes

* add green color to peak list names for better readability ([6ec65a1](https://github.com/dreamiurg/peakbagger-cli/commit/6ec65a1a0012016843c222974ff8a4db3e76a687))

# [0.6.0](https://github.com/dreamiurg/peakbagger-cli/compare/v0.5.0...v0.6.0) (2025-10-21)


### Features

* improve peak lists formatting in info command ([92006cf](https://github.com/dreamiurg/peakbagger-cli/commit/92006cf83fc755f3a6c580a5875012e9d2f56f8d)), closes [#1](https://github.com/dreamiurg/peakbagger-cli/issues/1)

# [0.5.0](https://github.com/dreamiurg/peakbagger-cli/compare/v0.4.0...v0.5.0) (2025-10-21)


### Features

* add ascent count to peak info command ([267b003](https://github.com/dreamiurg/peakbagger-cli/commit/267b0039c3ec7d366bfc1cf53dbd6b320fcbeae9))

# [0.4.0](https://github.com/dreamiurg/peakbagger-cli/compare/v0.3.0...v0.4.0) (2025-10-21)


### Features

* add --quiet flag to suppress informational messages ([7f9c58c](https://github.com/dreamiurg/peakbagger-cli/commit/7f9c58c7b733511a7e49c35f5a98531739e04f69))

# CHANGELOG

<!-- version list -->

## v0.3.0 (2025-10-20)

### Bug Fixes

- Add URLs to peak list output
  ([`773b39a`](https://github.com/dreamiurg/peakbagger-cli/commit/773b39a4276e3a57e80a01e0247364f1af2ea1cb))

- Correct ascent list sorting and clean date parsing
  ([`275fe29`](https://github.com/dreamiurg/peakbagger-cli/commit/275fe29617fe4e0d6080587e2b099fd186241bf4))

### Chores

- Update uv.lock after version bump
  ([`26387cc`](https://github.com/dreamiurg/peakbagger-cli/commit/26387cc4ab29dc0f33207e4d7fca7441c4c457a2))

### Documentation

- Update output examples in README and add documentation checklist
  ([`73f4bd2`](https://github.com/dreamiurg/peakbagger-cli/commit/73f4bd2cd3b1cb90d332dcd0b8db40867ef1ae65))

### Features

- Add Location, Range, and Elevation columns to search results
  ([`fd70c18`](https://github.com/dreamiurg/peakbagger-cli/commit/fd70c18efe0a5bb334ae768f5653294e44f2911f))

- Add peak lists and route information to info command
  ([`4ffd353`](https://github.com/dreamiurg/peakbagger-cli/commit/4ffd353d30cd0fc8d6eb70480ddf067e85023263))


## v0.2.0 (2025-10-20)

### Bug Fixes

- Add URL to Peak JSON output
  ([`59c8f93`](https://github.com/dreamiurg/peakbagger-cli/commit/59c8f9353475300d93863ced1f3fb60b2be36514))

### Chores

- Set up python-semantic-release for version management
  ([`688e3a5`](https://github.com/dreamiurg/peakbagger-cli/commit/688e3a51b6202f1f1b4de192bd5dfe1c06ba328f))

### Documentation

- Add CLAUDE.md with project-specific AI assistant instructions
  ([`e0fe2d7`](https://github.com/dreamiurg/peakbagger-cli/commit/e0fe2d71bd986c5ae6d6797e0ac326b7d8d6e03d))

- Streamline documentation and remove redundancy
  ([`e3e9cb2`](https://github.com/dreamiurg/peakbagger-cli/commit/e3e9cb28b9dee944d2f1b4d8b737bd01829b854e))

### Features

- Add comprehensive type annotations throughout codebase
  ([`1c2e922`](https://github.com/dreamiurg/peakbagger-cli/commit/1c2e9229a5b94de6b13fdc05e4d65e18a74ef987))

- Add PeakBagger URLs to search and info command output
  ([`e93841a`](https://github.com/dreamiurg/peakbagger-cli/commit/e93841a96b91886d473d2c9ae1e6be87fe0c2304))


## v0.1.0 (2025-10-20)

- Initial Release
