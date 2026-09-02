# 🧾 Changelog

All notable changes in this project will be documented in this file.


## [4.1.2](https://github.com/omnixys/observability-python/compare/v4.1.1...v4.1.2) (2026-09-02)

### Ci

* **Ci:** add setup-uv to release job for uv lock in prepare cmd ([](https://github.com/omnixys/observability-python/commit/fdf6abbf459ff7e5855404400f52d2c55f4f06a1))
* **Ci:** pin conventional-changelog-conventionalcommits to v9 for release-notes-generator compat ([](https://github.com/omnixys/observability-python/commit/fb34b3c5ee65f186c85558150b3827d8bac2c77a))

### Deps

* **Deps:** update omnixys deps ([](https://github.com/omnixys/observability-python/commit/3f64e33ce155fa55e2114a8bcdfc68872f1659ea))

### Other

* **Other:** Merge branch 'main' of https://github.com/omnixys/observability-python ([](https://github.com/omnixys/observability-python/commit/89a225edc5b0a0d067f519db0cfeb873f70c6cbf))
* **Other:** Merge pull request #1 from omnixys/migration/uuid-v7 ([](https://github.com/omnixys/observability-python/commit/2b58c7a46008d75160011cbfd5f530df1827e361)), closes [#1](https://github.com/omnixys/observability-python/issues/1)
* **Other:** Update release.config.js ([](https://github.com/omnixys/observability-python/commit/fc1004c4d9c4535722d0eeaeaa3c12adec9a7d04))
* **Other:** Update release.yml ([](https://github.com/omnixys/observability-python/commit/a623c8247c0439bd8cc8bb56396d8717a73911e2))

### Packaging

* **Packaging:** move package version to pyproject.toml and align release workflow ([](https://github.com/omnixys/observability-python/commit/e9f5e394be3f2643a435b384dd2f4c45205cd666))

### Release

* **Release:** Update release.config.js ([](https://github.com/omnixys/observability-python/commit/88727c889f1cee47939499163b67f4b2bcfeb7cb))
* **Release:** Update release.yml ([](https://github.com/omnixys/observability-python/commit/a3bf9df0a1c21919a013d6e2fbe0a04e7f4c7677))

## [4.1.1](https://github.com/omnixys/observability-python/compare/v4.1.0...v4.1.1) (2026-09-02)


### Bug Fixes

* **ci:** publish tagged release to PyPI ([6406a5a](https://github.com/omnixys/observability-python/commit/6406a5abbf81d3e4a0835071b73a6ebf6e240172))

# [4.1.0](https://github.com/omnixys/observability-python/compare/v4.0.1...v4.1.0) (2026-08-28)


### Features

* **logging:** keep debug logs visible in loki while console stays on info ([1fa9f6b](https://github.com/omnixys/observability-python/commit/1fa9f6b86de5d4cd2ee9ae4d6e903c449651e45f))

## [4.0.1](https://github.com/omnixys/observability-python/compare/v4.0.0...v4.0.1) (2026-08-22)


### Bug Fixes

* **dir:** remove target dir ([1de9af2](https://github.com/omnixys/observability-python/commit/1de9af2bdf7ddcc64ee05f572ecc2f3470b4be3f))

# [4.0.0](https://github.com/omnixys/observability-python/compare/v3.0.0...v4.0.0) (2026-08-03)


### Features

* **logging:** set root log level before attaching OTLP handler ([6110baa](https://github.com/omnixys/observability-python/commit/6110baa3bf6aad7a3ea6a64747dd718075162af9))

# [3.0.0](https://github.com/omnixys/observability-python/compare/v2.0.4...v3.0.0) (2026-07-28)


### Bug Fixes

* **ci:** Update ci.yaml ([afd413a](https://github.com/omnixys/observability-python/commit/afd413aff3310a69dd58ce56ebbc6c847ad2f664))
* **lint:** resolve all ruff lint violations ([b3128ed](https://github.com/omnixys/observability-python/commit/b3128ed70435052e3d81c0d2c9677207ed27e3b4))
* **observability:** update BatchLogRecordProcessor import for newer opentelemetry SDK ([c693cfc](https://github.com/omnixys/observability-python/commit/c693cfc978275b8559901cc9a820f249de0778bf))


### Features

* **logging:** enrich structured log context with request_id, tenant_id, actor_id ([a5bbe37](https://github.com/omnixys/observability-python/commit/a5bbe37714c3785a4bdaef5a883b366c190599a3))
* **observability:** add enabled, sampling_probability and log_level params ([aa57beb](https://github.com/omnixys/observability-python/commit/aa57beb350bd7858226b27abccad9c0f6db0dd7b))
* **observability:** add OTel log exporter to Python logging ([3738c7a](https://github.com/omnixys/observability-python/commit/3738c7a282aa9ddb559ebe3f2d86995048e47055))
* **observability:** configure canonical OTLP logging ([d00d72e](https://github.com/omnixys/observability-python/commit/d00d72e5d41f1a41e0be3ad733ca709cb6813a60))

## [2.0.4](https://github.com/omnixys/observability-python/compare/v2.0.3...v2.0.4) (2026-07-22)


### Bug Fixes

* **publish:** add uv build before uv publish ([d5aa1fa](https://github.com/omnixys/observability-python/commit/d5aa1fa58a97432ebd70926451eb74a6916333ee))

## [2.0.3](https://github.com/omnixys/observability-python/compare/v2.0.2...v2.0.3) (2026-07-22)


### Bug Fixes

* **publish:** replace gh release upload with uv publish to PyPI ([420ef67](https://github.com/omnixys/observability-python/commit/420ef6724596d9fb311e7af3c1a0d17d7b151d2a))

## [2.0.2](https://github.com/omnixys/observability-python/compare/v2.0.1...v2.0.2) (2026-07-22)


### Bug Fixes

* **release:** add @semantic-release/exec to update __version__ in __init__.py ([969ed6f](https://github.com/omnixys/observability-python/commit/969ed6f6b6725cd611b6f73aad36242d24c6b97c))

## [2.0.1](https://github.com/omnixys/observability-python/compare/v2.0.0...v2.0.1) (2026-07-22)


### Bug Fixes

* **cicd:** use version comparison for release detection ([eab84dd](https://github.com/omnixys/observability-python/commit/eab84ddbc0ff4a8563537204fdcba19058b8b7af))

# [2.0.0](https://github.com/omnixys/observability-python/compare/v1.1.1...v2.0.0) (2026-07-22)

# Changelog

All notable changes in this project will be documented in this file.


## [1.1.1](https://github.com/omnixys/observability-python/compare/v1.1.0...v1.1.1) (2026-07-22)

## [1.0.2](https://github.com/omnixys/observability-python/compare/v1.0.1...v1.0.2) (2026-07-22)

## [1.0.1](https://github.com/omnixys/observability-python/compare/v1.0.0...v1.0.1) (2026-07-15)

## 1.0.0 (2026-07-15)
