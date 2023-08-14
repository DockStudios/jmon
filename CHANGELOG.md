# Changelog

# [4.2.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.1.0...v4.2.0) (2023-08-14)


### Features

* Add coloring of 'latest status' column in run list ([d280c18](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/d280c18a917fe8000775c190eb1b98cc049c7cfb)), closes [#72](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/72)
* Add colors to check list row based on average success percentage ([4f6efe9](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/4f6efe9cd94e27b3cd5641179628a6007bfc3556)), closes [#72](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/72)

# [4.1.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.0.3...v4.1.0) (2023-08-13)


### Features

* Add API endpoint with details about agent queue counts ([6630c0e](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/6630c0ed13c61d7ed63ef2d089d99c17c0d56e32)), closes [#75](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/75)
* Add status page with agent count by queue ([29e688c](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/29e688c2bd434add4c3d0cb5ae53d78b55397f1e)), closes [#75](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/75)
* Show error in UI when there are no agents serving the default queue ([f0a388a](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/f0a388af980ffc11b6f800068da95281f56a6ff2)), closes [#75](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/75)

## [4.0.3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.0.2...v4.0.3) (2023-08-12)


### Bug Fixes

* Add protection around passing invalid action as string value to action ([8c2c51e](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/8c2c51ee4bfc3f2c2274b68fbfe6a562510d86e4))
* Create unified instance of log handling for run and steps. ([4f142ee](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/4f142eeb22232b4fa4577cc32a01c45054e051fe)), closes [#71](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/71)
* Disable logging of root step ([4e4fa3a](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/4e4fa3aad893be30ede1749789942622717e4d16)), closes [#71](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/71)

## [4.0.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.0.1...v4.0.2) (2023-08-12)


### Bug Fixes

* **docs:** Add validation of YAML of dostring examples and fix incorrect find indentation ([33f3264](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/33f326428148a390d27b9bea3f302b79bccba786)), closes [#70](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/70)

## [4.0.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.0.0...v4.0.1) (2023-08-11)


### Bug Fixes

* Fix JSON check description when a selector is not provided ([10507bb](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/10507bb0b8ada2e8b4c951c684a2b35f833e9a95))

# [4.0.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v3.0.2...v4.0.0) (2023-08-11)


### Features

* Add support for matching JSON response using selectors and support partial matches of value ([5912b6d](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/5912b6d5b3fd84be5d8430751bf7f23ac5e28383)), closes [#70](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/70)


### BREAKING CHANGES

* The original format of JSON response checking is not longer supported.
```
 - check:
    json: {"ok": true}
```
is no longer supported and must now be
 - check:
    json:
      equals: {"ok": true}

## [3.0.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v3.0.1...v3.0.2) (2023-08-11)


### Bug Fixes

* Add configuration for maximum tasks per worker, to force restart of worker and avoid memory leaks ([1ee001e](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/1ee001ed4f8a4d82479aa0466805392d80663f7e))
* Create singleton instance of ArtifactStorage class to avoid additional memory and possible leaks in boto3 ([72fb622](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/72fb6222694b9a1583ef707dd875fb02a578da70)), closes [#71](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/71)

## [3.0.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v3.0.0...v3.0.1) (2023-08-11)


### Bug Fixes

* Add missing attributes kwarg for base methods for plugins ([5da3d35](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/5da3d355385bc3a38ed76e7f00777beee1b4eb8e))

# [3.0.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v2.1.0...v3.0.0) (2023-08-11)

### Breaking Changes

* Add 'attributes' argument to plugins calls. ([2263903](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/2263903998101208e7fa42f3b7279de8c750343e)), closes [#58](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/67)

### Bug Fixes

* Add restart always to docker containers in docker-compose definition ([13c4005](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/13c4005677fbb9a01d399c54075ef2a429445848)), closes [#67](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/67)
* Add semantic-release config ([2203aba](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/2203aba64c777e2ba6b87171e88df1f613c14f95)), closes [#65](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/65)


### Features

* Add /api/v1/version endpoint to return current version of JMon instance ([21e14bd](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/21e14bd64e5c35047a2ae0780c3d91301888457a)), closes [#66](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/66)
* Add attributes to task defintion, which can be set during creation and displayed in API for task details ([c86b80b](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/c86b80bece052ffa5682e0bdb1de9fd9b4975f93)), closes [#58](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/58)
