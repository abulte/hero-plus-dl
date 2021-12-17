# hero-plus-dl

Download (free!) your photos/videos from GoPro Hero Plus service.

This is quite unpolished but it did the job for a one time thing.

You'll need to tell Firefox to download the file and remember the option the first time it pops up.

:warning: Don't kill the browser until everyting is downloaded.

```shell
GP_USER=gopro_user GP_PASSWORD=gopro_password python cli.py download
```

## Known issues

- Does not handle media library pagination (100 max I guess, I only had 88 at the time) ; should be easy to add if needed.
- Does not handle pictures (Firefox does not download them by default)
