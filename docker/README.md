Build a Docker container for the legacyhalos project.
=====================================================

```
docker pull legacysurvey/legacypipe:DR9.8.3
docker build . -t legacysurvey/legacyhalos
docker push legacysurvey/legacyhalos:latest

docker tag legacysurvey/legacyhalos:latest legacysurvey/legacyhalos:v0.1
docker push legacysurvey/legacyhalos:v0.1
```

To enter the container (with a shell prompt) on a laptop do:
```
docker pull legacysurvey/legacyhalos:latest
docker run -it legacysurvey/legacyhalos:latest
```

Or at NERSC:
```
shifterimg pull docker:legacysurvey/legacyhalos:v0.1
shifterimg pull docker:legacysurvey/legacyhalos:latest
shifter --image docker:legacysurvey/legacyhalos:latest bash
```
