# Interactive HTML with Archify

Use the locally available Archify skill and CLI. Read the installed `SKILL.md` and its repository authoring guide for the selected diagram type. If the runtime is unavailable, identify the missing capability and offer Mermaid source as an alternate artifact. For bell-harness, provision it with `bin/setup --with-archify` on request. [Upstream installation options](https://github.com/tt-a1i/archify#installation-options)

For a real repository, cite source ranges from the pinned checkout on the primary elements. Use the checkout's repository identity with credentials removed. Choose local-only links for source that should stay local. Keep private source text and credentials out of the exported HTML.

Run the installed release's documented validation command. Archify's repository authoring workflow uses:

```sh
node "<archify-skill>/bin/archify.mjs" finalize "<type>" "<candidate.json>" "<diagram.html>" --repo-root "<repository>" --quality showcase --json
```

Use the quality profile recorded in the candidate. Record the actual gate results. If a browser gate fails because the browser cannot start, use another available browser to inspect the artifact and report the two results separately. Preserve the browser's security settings.

Open the HTML at the intended viewing width. Select a representative node and check that the viewer opens the expected connections and source evidence. On narrow screens, check whether the main path and important branch remain accessible. Keep the editable candidate alongside the HTML in the requested output location.
