# Changelog

## [4.11.4](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.11.3...v4.11.4) (2023-09-09)


### Bug Fixes

* **deps:** bump pillow from 9.4.0 to 10.0.0 ([c690bb7](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/c690bb7cfb6277718c89e4d26c0f3aad85057e42))

## [4.11.3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.11.2...v4.11.3) (2023-09-09)


### Bug Fixes

* **deps:** bump @testing-library/jest-dom from 5.16.5 to 6.1.3 in /ui ([c138cad](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/c138cad4cc038470673d5320b182aa2c7c5b43d7))

## [4.11.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.11.1...v4.11.2) (2023-09-09)


### Bug Fixes

* **deps:** bump @mui/x-data-grid from 5.17.25 to 6.12.1 in /ui ([30e00fd](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/30e00fdc11ce064fd0f8d5c89a6f8df7d9d07960))

## [4.11.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.11.0...v4.11.1) (2023-09-02)


### Bug Fixes

* Update dependabot config to mark as fix, so package changes are released ([ff80743](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/ff80743b7d835d95e4045f17b1f6325469f8f2c4))

# [4.11.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.10.2...v4.11.0) (2023-09-01)


### Bug Fixes

* Fix output in run with available client types with list of names, rather than stringified enums ([f99d0bd](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/f99d0bd65ccf4537315b2744d7f177dc5cfc9751)), closes [#10](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/10)


### Features

* Initial draft showing run graph with steps and status of steps in run overview ([34b8eae](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/34b8eae370cd4336d924e1db16a6f8d41cfbcd53)), closes [#10](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/10)
* Store run steps with status in s3 ([8f8c1c9](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/8f8c1c99b788a6826c74606c58de46905303dc45)), closes [#10](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/10)

## [4.10.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.10.1...v4.10.2) (2023-08-31)


### Bug Fixes

* Return screenshot_on_error attribute in check API. ([a5c5ee3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/a5c5ee351678ed26ad03c8cf8eeff4b1c509696e)), closes [#98](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/98)

## [4.10.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.10.0...v4.10.1) (2023-08-31)


### Bug Fixes

* Fix bug where check URL step checks for None url ([ede79c5](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/ede79c53b4c36deccd035739367aa30ac9e30e93)), closes [#99](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/99)

# [4.10.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.9.0...v4.10.0) (2023-08-28)


### Features

* Add support for chrome headless mode, defaulting to legacy "chrome" headless mode with config to change this ([6ca56b1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/6ca56b1e203916d6210eb31a954e7a2944be436d)), closes [#95](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/95)
* Add support for firefox headless mode, which is enabled by default ([7410a5a](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/7410a5a8a7681962d0f32ff2bef49e7771855931)), closes [#95](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/95)
* Disable web caching in browsers ([efde07f](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/efde07f9d4deebc7e1572d338e80f3f1195a102c)), closes [#96](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/96)

# [4.9.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.8.0...v4.9.0) (2023-08-27)


### Bug Fixes

* Fix width of average success column in check list table ([a9f28df](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/a9f28df9bedb0ab75634c4b3f0d50aa10471b57d)), closes [#81](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/81)


### Features

* Add filtering of check names in check list view ([6ab00d1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/6ab00d1858829f021fd7bfafbd69ad5fc09ccbc1)), closes [#81](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/81)

# [4.8.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.7.1...v4.8.0) (2023-08-26)


### Features

* Add API key to functionality and add protection to API endpoints that create/modify checks ([f3cf9fc](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/f3cf9fcb2c15554047d4f02d3ae8991fa9856019)), closes [#21](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/21)

## [4.7.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.7.0...v4.7.1) (2023-08-26)


### Bug Fixes

* Stop checks being run on multiple workers from different queues. ([970bd37](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/970bd37c66da3b03dc1c3772bab2337728567b5f)), closes [#92](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/92)

# [4.7.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.6.0...v4.7.0) (2023-08-26)


### Bug Fixes

* Catch any exceptions thrown when performing goto request ([26237e9](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/26237e9998ede8e2956dd6bf0ae6c063eb5448cb)), closes [#90](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/90)
* Ensure browser is closed if selenium fails to contact browser ([a58a876](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/a58a876e4fc17edf6783ff5b13d5f7634b246774)), closes [#93](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/93)


### Features

* Add experimental browser caching functionality with new config to enable it ([e3bd48e](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/e3bd48e8a17b4796e54399de5b0643c8b1e99913)), closes [#90](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/90)
* Automatically switch run client type to cached browser, if present ([d1bb2f6](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/d1bb2f61605358963987e2ff2837e438e93b25ba)), closes [#90](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/90)

# [4.6.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.5.2...v4.6.0) (2023-08-24)


### Bug Fixes

* Fix example notification plugin, removing incorrect argument 'attributes' to on_check_queue_timeout ([4158358](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/4158358c92119f59bfe92139abd699f8beb4d2c7)), closes [#89](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/89)
* Fix slack example notification plugin, passing empty 'attributes' to post_message function from on_check_queue_timeout ([3831520](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/3831520c98fbb3545df3f2b4d6925cb1741aa8b6)), closes [#89](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/89)


### Features

* Create deadletter queue for expired tasks in rabbitmq broker. ([9388b2f](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/9388b2fdbe320bf5b95be9ec8793a4de1640a61d)), closes [#89](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/89)

## [4.5.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.5.1...v4.5.2) (2023-08-23)


### Bug Fixes

* Cache display per worker process, ensuring the display is closed on worker shutdown ([f429484](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/f429484d999e73a10758fb873ef16dca89426cb5)), closes [#88](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/88)
* Ensure XVFB display is closed after each test ([09e57b8](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/09e57b893b768405557c2329f328f711029e2b80)), closes [#88](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/88)

## [4.5.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.5.0...v4.5.1) (2023-08-21)


### Bug Fixes

* Create boto2 session instance of ArtifactStorage. ([6b2c177](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/6b2c177f72c906a2faa4da18206aeb5a36a3a9a1)), closes [#80](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/80)

# [4.5.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.4.0...v4.5.0) (2023-08-20)


### Features

* Add support for custom callable plugins within steps. ([24e80ac](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/24e80ac92175766414dddfe0c9d983b3149a5eb0)), closes [#84](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/84) [#85](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/85)
* Add support for passing method, headers and body to goto step for non-browser tests ([17c00ec](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/17c00ec661ff6b698ddfa8b73e678d1a0d256e39)), closes [#84](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/84)
* Add support for setting runtime variables in a run in callable plugins ([2016b75](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/2016b7513f4a1b7f9b721e5791d1d722a9c24558)), closes [#84](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/84)
* Support injection of run variables into step configs ([b02ed2d](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/b02ed2db4a737611c1588fc60cc9d5d62a6f3994)), closes [#84](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/84)

# [4.4.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.3.2...v4.4.0) (2023-08-17)


### Features

* Add filtering of results API endpoint average success to provide timeframes. ([006b2f3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/006b2f39b74f18db9daad73b461c47c39f5295b5)), closes [#73](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/73)
* Add UI selection in check list to select result timeframe ([08897a3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/08897a37b86cf7afe4913de1c4cfac38ef50098d)), closes [#73](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/73)

## [4.3.2](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.3.1...v4.3.2) (2023-08-17)


### Bug Fixes

* Fix ocassional exceptions when loading an artifact endpoint ([e0c2878](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/e0c2878b7fad6ad5e4fd524e292cdbef829583d7)), closes [#80](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/80)

## [4.3.1](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.3.0...v4.3.1) (2023-08-16)


### Bug Fixes

* Add check for size of attributes/steps fields when creating/updating check to ensure they are not too large ([36eeb06](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/36eeb0602201207642342052e43e3b3a5782026b)), closes [#79](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/79)
* **db:** Convert attributes columns to binary blobs, increaseing maximum size of steps and attributes ([e138d63](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/e138d63a022569cbd5c0a8d50bdfce85747dad9e)), closes [#79](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/79)

# [4.3.0](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/compare/v4.2.0...v4.3.0) (2023-08-14)


### Bug Fixes

* Add run column for trigger type, setting to scheduled for scheduler runs and manual for triggered runs through API. ([5eff698](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/5eff69852e9f82fc08dbdf212bbd6d0506ef7e91)), closes [#68](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/68)


### Features

* Add ability to trigger run in UI ([3dc5408](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/3dc5408637953e26439cab05894e3a66ecf49844)), closes [#68](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/68)
* Add API endpoint for querying manually triggered runs ([7edd834](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/7edd8349f6ddf7d92ece331ef4dc74a8ad9b5e64)), closes [#68](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/68)
* Add API endpoint to manually trigger run ([21f53c3](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/commit/21f53c30dee7b2f6ec581293e88a345b60592876)), closes [#68](https://gitlab.dockstudios.co.uk/pub/jmon/jmon/issues/68)

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
