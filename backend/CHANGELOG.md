# CHANGELOG


## v0.1.0 (2026-08-03)

### Bug Fixes

- Silence docker warning for deprecated AS syntax
  ([`942e8d0`](https://github.com/bmcivor/django-tipping/commit/942e8d06a75a58630f5c7a80bf50517b42a82513))

- **8**: Complete fixes from linting and quality checks
  ([`7929c1c`](https://github.com/bmcivor/django-tipping/commit/7929c1c699ff35370b4e80782335f4d0c108fe45))

### Chores

- Add in basic skeletons of README files
  ([`fab4e05`](https://github.com/bmcivor/django-tipping/commit/fab4e055471f81a817842682257cbb0b894040f8))

- Clean up old mess of old design
  ([`c2d2db7`](https://github.com/bmcivor/django-tipping/commit/c2d2db7724b7b486839e060515105f1b2202feca))

Let's start a bit more fresh, float some new docs for now.

- **12**: Update gitignore to latest template
  ([`21f245b`](https://github.com/bmcivor/django-tipping/commit/21f245b4deefaeb3dd4f78ce5921851115735992))

- **13**: Add MIT licence file
  ([`baff6d3`](https://github.com/bmcivor/django-tipping/commit/baff6d3d01b6ecdfe4381c01a103a29c68914b49))

### Features

- Add in basic django 4 application
  ([`5220375`](https://github.com/bmcivor/django-tipping/commit/52203757a5b2807ba92fbc69a2679baf49b9fccc))

Also includes a small users app which will be a modular implementation of user profiles etc.

- Add in basic python gitignore
  ([`b052b7c`](https://github.com/bmcivor/django-tipping/commit/b052b7c388c9076b70a38d20edd9c2eb750fc30d))

Shamelessly stolen from githubs public version of a python gitignore.

As the frontend goes in this will have to be expanded.

- Add in diagrams directory
  ([`044049b`](https://github.com/bmcivor/django-tipping/commit/044049b83ce4c5c58288ead78fe98bc36721ae7b))

- Add in inital basic Docker setup
  ([`1fab9db`](https://github.com/bmcivor/django-tipping/commit/1fab9dbafb2242441ea393ba34aec6fa95027453))

Not really doing anything here, just wanted to get a basic setup going that pulls and builds.

It won't run as the django webserver has not been installed yet.

- Add in initial scoping of modelling layer
  ([`16c0fa5`](https://github.com/bmcivor/django-tipping/commit/16c0fa5af02b4256ba8c1cc7be23716560a75172))

- Add in new database schema design
  ([`65e2980`](https://github.com/bmcivor/django-tipping/commit/65e29805fe5b267827fffca9759ae598a5c37247))

Super high level and it will end up being way larger. This is an initial setup to get things going.

- Add in poetry for dependency management
  ([`bfd3241`](https://github.com/bmcivor/django-tipping/commit/bfd324168e4c872d5670ad7b587497f40d79b89d))

- Initial commit
  ([`5890de5`](https://github.com/bmcivor/django-tipping/commit/5890de5c8074be26dbd871a214fc97aa154ecdf8))

- **10**: Add in python semantic release
  ([`9edbfb4`](https://github.com/bmcivor/django-tipping/commit/9edbfb4dd52640b556aa0fb0dc7fb2af0c960469))

- **14**: Recreate Django app
  ([`0ca4200`](https://github.com/bmcivor/django-tipping/commit/0ca420042e3cf1f01f918ddc7b8fd0fc64d356fb))

With a bit of a redesign to incoporate how there will be a split of ownership between the backend
  and frontend.

With some test framework handling from the docker level.

- **15**: Add in basic django docker ignore file
  ([`4061b21`](https://github.com/bmcivor/django-tipping/commit/4061b215225b0ccd2818165936969816d5bf6f32))

- **16**: Add in basic migration service
  ([`a062c3b`](https://github.com/bmcivor/django-tipping/commit/a062c3b0d57dcba03f9ba0b619ebf5ddab883a10))

- **2**: Migrate packaging from poetry to uv
  ([`9d5cf18`](https://github.com/bmcivor/django-tipping/commit/9d5cf1846d0bbf4abe8ce2ecf2ff23e81f0d3e46))

- **3**: Add in Django 6
  ([`93857a9`](https://github.com/bmcivor/django-tipping/commit/93857a9d2c0319cc7e0146c94f26b8ee5d6c36f0))

- **3**: Add in Django 6
  ([`b93e707`](https://github.com/bmcivor/django-tipping/commit/b93e707234a790c46559c1d2ae2076d5482a9fda))

- **4**: Add in postgres db service for local dev
  ([`1af0020`](https://github.com/bmcivor/django-tipping/commit/1af0020ceeaf52575c3a0b04a3872151e555c392))

- **4**: Update db definitions in django settings
  ([`c827084`](https://github.com/bmcivor/django-tipping/commit/c8270844b871914987dbd978806ade8109a72b75))

- **6**: Add in vite / typescript / react scaffold
  ([`9aefc2e`](https://github.com/bmcivor/django-tipping/commit/9aefc2e7412baac12403f4e010f793d1c07c4df5))

- **7**: Add in test harness for backend and frontend suites
  ([`bdfa35b`](https://github.com/bmcivor/django-tipping/commit/bdfa35ba95a63137b0f601707cc29dd50c969885))

- **8**: Add in linting and formatting checks to pipeline
  ([`341e827`](https://github.com/bmcivor/django-tipping/commit/341e82745a578a37236321e99388ba9371d02528))

For the backend:

- mypy - ruff

This required adding in django-stubs for mypy to work with Django's magic.

For the frontend:

- prettier

- **9**: Add in Jenkinsfile for running CI job
  ([`6c78af5`](https://github.com/bmcivor/django-tipping/commit/6c78af5c3b82ce62ca1c715fbb754f99f230c376))
