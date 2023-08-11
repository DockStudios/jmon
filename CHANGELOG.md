# Changelog

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
