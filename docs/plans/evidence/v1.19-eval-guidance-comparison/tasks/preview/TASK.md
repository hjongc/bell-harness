# Package the preview template

The preview CLI is built from this checkout and installed into a separate directory. Fix the build and CLI in `build.py` and `preview.py`. Preserve the source template in `preview.txt`.

From this checkout, run `python3 build.py INSTALL_DIRECTORY` with a fresh installation directory. The installed directory must contain `preview.py` and its `preview.txt` sidecar. From any working directory, `python3 INSTALL_DIRECTORY/preview.py TITLE` must read the installed sidecar as UTF-8 and write its contents to stdout with `{title}` replaced by the provided title. A change to the source template after the build must leave this installation's output unchanged.

When the installed template is missing, exit 2, write a diagnostic containing `missing installed template` to stderr, and leave stdout empty.

Use the Python standard library and keep build outputs in the supplied installation directory. Exercise the normal entry points in a temporary directory and report your verification commands and results.
