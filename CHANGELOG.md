# [1.7.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.6.3...v1.7.0) (2025-10-24)


### Features

* add field parity and URLs to ascent show text output ([#18](https://github.com/dreamiurg/peakbagger-cli/issues/18)) ([5718c82](https://github.com/dreamiurg/peakbagger-cli/commit/5718c82eaeae17e83599cae22c29335f4daf8df2))

## [1.6.3](https://github.com/dreamiurg/peakbagger-cli/compare/v1.6.2...v1.6.3) (2025-10-24)


### Bug Fixes

* parse ascent rows with nested tables in route icons ([#17](https://github.com/dreamiurg/peakbagger-cli/issues/17)) ([ec99fd1](https://github.com/dreamiurg/peakbagger-cli/commit/ec99fd13790727fbe154e29f2e9ddeb3b161ab16))

## [1.6.2](https://github.com/dreamiurg/peakbagger-cli/compare/v1.6.1...v1.6.2) (2025-10-24)


### Bug Fixes

* updated uv.lock ([#15](https://github.com/dreamiurg/peakbagger-cli/issues/15)) ([d94a16c](https://github.com/dreamiurg/peakbagger-cli/commit/d94a16c2912ed0f4c58cd280b442cb7b10a384fc))

## [1.6.1](https://github.com/dreamiurg/peakbagger-cli/compare/v1.6.0...v1.6.1) (2025-10-24)


### Bug Fixes

* sort ascents by date before applying limit ([#14](https://github.com/dreamiurg/peakbagger-cli/issues/14)) ([9b6c76c](https://github.com/dreamiurg/peakbagger-cli/commit/9b6c76c3ea3b7c8d3b6bd794bf1bf7c30cda4f84))

# [1.6.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.5.0...v1.6.0) (2025-10-24)


### Features

* remove table borders and prevent text truncation ([#13](https://github.com/dreamiurg/peakbagger-cli/issues/13)) ([981f647](https://github.com/dreamiurg/peakbagger-cli/commit/981f64765a27b1c752c0fbc961d398b993b72d93))

# [1.5.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.4.0...v1.5.0) (2025-10-24)


### Bug Fixes

* disable text wrapping in all Rich tables and fix JSON output ([#12](https://github.com/dreamiurg/peakbagger-cli/issues/12)) ([3377472](https://github.com/dreamiurg/peakbagger-cli/commit/33774724b423e7293c62de9362598112667b1396))


### Features

* additional --verbose and --debug logging options ([#8](https://github.com/dreamiurg/peakbagger-cli/issues/8)) ([1faa61c](https://github.com/dreamiurg/peakbagger-cli/commit/1faa61c823783fe32c9a44efece5fe2e69a3cc86))
* remove status messages and make --debug require --verbose ([#11](https://github.com/dreamiurg/peakbagger-cli/issues/11)) ([336ed7a](https://github.com/dreamiurg/peakbagger-cli/commit/336ed7acbab07bf72537851d806fdb17bef01824))

# [1.4.0](https://github.com/dreamiurg/peakbagger-cli/compare/v1.3.0...v1.4.0) (2025-10-22)


### Features

* add --dump-html option to dump raw HTML to stdout ([#7](https://github.com/dreamiurg/peakbagger-cli/issues/7)) ([e48bb18](https://github.com/dreamiurg/peakbagger-cli/commit/e48bb181713e835580350041f950ff8aee1679c1))

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

## v1.9.1 (2025-11-01)

### Bug Fixes

- Correct PyPI package name and GitHub URLs in README
  ([#45](https://github.com/dreamiurg/peakbagger-cli/pull/45),
  [`83fe830`](https://github.com/dreamiurg/peakbagger-cli/commit/83fe830102dbbef27ba62513ba21b9c6dfe5e35b))


## v1.9.0 (2025-11-01)

### Continuous Integration

- **deps**: Bump actions/checkout from 4 to 5
  ([#42](https://github.com/dreamiurg/peakbagger-cli/pull/42),
  [`65abe17`](https://github.com/dreamiurg/peakbagger-cli/commit/65abe17b3c42fe4920c994d921188d825f0e8052))

- **deps**: Bump amannn/action-semantic-pull-request from 5 to 6
  ([#43](https://github.com/dreamiurg/peakbagger-cli/pull/43),
  [`0c5b20d`](https://github.com/dreamiurg/peakbagger-cli/commit/0c5b20d66ab9a01a048ee9919686fc67ed9b617c))

- **deps**: Bump astral-sh/setup-uv from 5 to 7
  ([#41](https://github.com/dreamiurg/peakbagger-cli/pull/41),
  [`43e2b4c`](https://github.com/dreamiurg/peakbagger-cli/commit/43e2b4c77d0d64a940cc0ca04978e9ecf77891ef))

### Documentation

- Add PyPI badges to README ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))

- Add reference to GitHub App setup guide for maintainers
  ([#40](https://github.com/dreamiurg/peakbagger-cli/pull/40),
  [`73851f8`](https://github.com/dreamiurg/peakbagger-cli/commit/73851f839739e72a929b467c2194fc4398acbe95))

- Convert file name references to links in CLAUDE.md
  ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))

- Remove license and typed badges from README
  ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))

- Remove maintainer-only sections from CONTRIBUTING.md
  ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))

- Simplify CONTRIBUTING.md ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))

### Features

- Add automated PyPI publishing ([#44](https://github.com/dreamiurg/peakbagger-cli/pull/44),
  [`1ba35b8`](https://github.com/dreamiurg/peakbagger-cli/commit/1ba35b816aa4e9cf5361d1f5e88c2bcb4b49a37c))


## v1.8.0 (2025-10-25)

### Bug Fixes

- Improve User-Agent string clarity ([#33](https://github.com/dreamiurg/peakbagger-cli/pull/33),
  [`5d95b6e`](https://github.com/dreamiurg/peakbagger-cli/commit/5d95b6ecb38eec0365d243bf67c4ff239806c14a))

- Remove invalid changelog placeholder from release commit message
  ([#34](https://github.com/dreamiurg/peakbagger-cli/pull/34),
  [`0730d84`](https://github.com/dreamiurg/peakbagger-cli/commit/0730d84e6633d09a58f36a446c95d2991935f160))

- Remove persist-credentials false to allow git push with app token
  ([#37](https://github.com/dreamiurg/peakbagger-cli/pull/37),
  [`afba7e9`](https://github.com/dreamiurg/peakbagger-cli/commit/afba7e91fa071eccf14036f4f6ebdbfa7a857b4a))

- Update User-Agent URL to correct repository
  ([#39](https://github.com/dreamiurg/peakbagger-cli/pull/39),
  [`6ec81e4`](https://github.com/dreamiurg/peakbagger-cli/commit/6ec81e437814083ff4ea2ca5d7ca0967a7a3af13))

### Chores

- Add py.typed marker for PEP 561 compliance
  ([#20](https://github.com/dreamiurg/peakbagger-cli/pull/20),
  [`8fbde73`](https://github.com/dreamiurg/peakbagger-cli/commit/8fbde73624df31544823082a571d155a5d259cca))

- Ignore docs/plans directory ([#31](https://github.com/dreamiurg/peakbagger-cli/pull/31),
  [`c243df1`](https://github.com/dreamiurg/peakbagger-cli/commit/c243df102b32a58222ac2491cc975ead5135927e))

- Migrate from Node.js semantic-release to Python equivalents
  ([#27](https://github.com/dreamiurg/peakbagger-cli/pull/27),
  [`6d7e55b`](https://github.com/dreamiurg/peakbagger-cli/commit/6d7e55b0ab19801fa9de663b4b0174b664dd1cdb))

- **deps-dev**: Bump the semantic-release group with 3 updates
  ([#26](https://github.com/dreamiurg/peakbagger-cli/pull/26),
  [`cc7600b`](https://github.com/dreamiurg/peakbagger-cli/commit/cc7600bc6051fc20e64d15bd2ba15e628d35ff21))

### Continuous Integration

- Add badges and GitHub Actions CI workflow
  ([#20](https://github.com/dreamiurg/peakbagger-cli/pull/20),
  [`8fbde73`](https://github.com/dreamiurg/peakbagger-cli/commit/8fbde73624df31544823082a571d155a5d259cca))

- Add Dependabot configuration for automated dependency updates
  ([#22](https://github.com/dreamiurg/peakbagger-cli/pull/22),
  [`d6aaa56`](https://github.com/dreamiurg/peakbagger-cli/commit/d6aaa56039074710f5450d3f25096e171d145bee))

- Add GitHub Actions workflow with cross-platform testing
  ([#20](https://github.com/dreamiurg/peakbagger-cli/pull/20),
  [`8fbde73`](https://github.com/dreamiurg/peakbagger-cli/commit/8fbde73624df31544823082a571d155a5d259cca))

- Improve dependency management and caching
  ([#22](https://github.com/dreamiurg/peakbagger-cli/pull/22),
  [`d6aaa56`](https://github.com/dreamiurg/peakbagger-cli/commit/d6aaa56039074710f5450d3f25096e171d145bee))

- Optimize GitHub Actions performance ([#30](https://github.com/dreamiurg/peakbagger-cli/pull/30),
  [`2ebba16`](https://github.com/dreamiurg/peakbagger-cli/commit/2ebba168bc964e4ccad13afc7e20fdedad1a64da))

- Skip CI when only .gitignore changes ([#32](https://github.com/dreamiurg/peakbagger-cli/pull/32),
  [`013b9bf`](https://github.com/dreamiurg/peakbagger-cli/commit/013b9bf4743846d4bfe02f589f1caa46af34682a))

- Upgrade uv action to v5 and enable dependency caching
  ([#22](https://github.com/dreamiurg/peakbagger-cli/pull/22),
  [`d6aaa56`](https://github.com/dreamiurg/peakbagger-cli/commit/d6aaa56039074710f5450d3f25096e171d145bee))

- **deps**: Bump actions/setup-node from 4 to 6
  ([#25](https://github.com/dreamiurg/peakbagger-cli/pull/25),
  [`3d88393`](https://github.com/dreamiurg/peakbagger-cli/commit/3d88393fb2e0f878729c0c1a9e559b74b47a9dd6))

- **deps**: Bump actions/setup-python from 5 to 6
  ([#24](https://github.com/dreamiurg/peakbagger-cli/pull/24),
  [`b4baf46`](https://github.com/dreamiurg/peakbagger-cli/commit/b4baf46daae6452e5b3b02c2e5e5656f5427a713))

- **deps**: Bump codecov/codecov-action from 4 to 5
  ([#23](https://github.com/dreamiurg/peakbagger-cli/pull/23),
  [`4bd870b`](https://github.com/dreamiurg/peakbagger-cli/commit/4bd870baa2e129ba26fa1586c51f3f6c8eb14b34))

### Documentation

- Add architecture diagrams and developer cookbook
  ([#29](https://github.com/dreamiurg/peakbagger-cli/pull/29),
  [`97ccf10`](https://github.com/dreamiurg/peakbagger-cli/commit/97ccf10908945d3cb54c219847858c60212b6621))

- Add badges to README ([#20](https://github.com/dreamiurg/peakbagger-cli/pull/20),
  [`8fbde73`](https://github.com/dreamiurg/peakbagger-cli/commit/8fbde73624df31544823082a571d155a5d259cca))

- Streamline documentation for clarity and automation
  ([#28](https://github.com/dreamiurg/peakbagger-cli/pull/28),
  [`28c6181`](https://github.com/dreamiurg/peakbagger-cli/commit/28c6181c0e8e100c17e4c066b33328544b560379))

- Update README with current CLI output examples
  ([#21](https://github.com/dreamiurg/peakbagger-cli/pull/21),
  [`fb6159e`](https://github.com/dreamiurg/peakbagger-cli/commit/fb6159ef3cddab01fda1e26f52d87f136f1f4965))

### Features

- Use GitHub App for semantic-release to bypass branch protection
  ([#36](https://github.com/dreamiurg/peakbagger-cli/pull/36),
  [`a2ef638`](https://github.com/dreamiurg/peakbagger-cli/commit/a2ef638db6080935bacff08b9abc331ceae09a34))

### Refactoring

- Address CodeRabbit feedback from PRs #14 and #17
  ([#19](https://github.com/dreamiurg/peakbagger-cli/pull/19),
  [`cc9053c`](https://github.com/dreamiurg/peakbagger-cli/commit/cc9053ca3f73b110e06268ff828efd4a2b9e0786))


## v0.3.0 (2025-10-20)

### Bug Fixes

* Add URLs to peak list output
  ([`773b39a`](https://github.com/dreamiurg/peakbagger-cli/commit/773b39a4276e3a57e80a01e0247364f1af2ea1cb))

* Correct ascent list sorting and clean date parsing
  ([`275fe29`](https://github.com/dreamiurg/peakbagger-cli/commit/275fe29617fe4e0d6080587e2b099fd186241bf4))

### Chores

* Update uv.lock after version bump
  ([`26387cc`](https://github.com/dreamiurg/peakbagger-cli/commit/26387cc4ab29dc0f33207e4d7fca7441c4c457a2))

### Documentation

* Update output examples in README and add documentation checklist
  ([`73f4bd2`](https://github.com/dreamiurg/peakbagger-cli/commit/73f4bd2cd3b1cb90d332dcd0b8db40867ef1ae65))

### Features

* Add Location, Range, and Elevation columns to search results
  ([`fd70c18`](https://github.com/dreamiurg/peakbagger-cli/commit/fd70c18efe0a5bb334ae768f5653294e44f2911f))

* Add peak lists and route information to info command
  ([`4ffd353`](https://github.com/dreamiurg/peakbagger-cli/commit/4ffd353d30cd0fc8d6eb70480ddf067e85023263))

## v0.2.0 (2025-10-20)

### Bug Fixes

* Add URL to Peak JSON output
  ([`59c8f93`](https://github.com/dreamiurg/peakbagger-cli/commit/59c8f9353475300d93863ced1f3fb60b2be36514))

### Chores

* Set up python-semantic-release for version management
  ([`688e3a5`](https://github.com/dreamiurg/peakbagger-cli/commit/688e3a51b6202f1f1b4de192bd5dfe1c06ba328f))

### Documentation

* Add CLAUDE.md with project-specific AI assistant instructions
  ([`e0fe2d7`](https://github.com/dreamiurg/peakbagger-cli/commit/e0fe2d71bd986c5ae6d6797e0ac326b7d8d6e03d))

* Streamline documentation and remove redundancy
  ([`e3e9cb2`](https://github.com/dreamiurg/peakbagger-cli/commit/e3e9cb28b9dee944d2f1b4d8b737bd01829b854e))

### Features

* Add comprehensive type annotations throughout codebase
  ([`1c2e922`](https://github.com/dreamiurg/peakbagger-cli/commit/1c2e9229a5b94de6b13fdc05e4d65e18a74ef987))

* Add PeakBagger URLs to search and info command output
  ([`e93841a`](https://github.com/dreamiurg/peakbagger-cli/commit/e93841a96b91886d473d2c9ae1e6be87fe0c2304))

## v0.1.0 (2025-10-20)

* Initial Release
