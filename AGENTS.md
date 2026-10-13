# Repository instructions

Mode: production. Stability: experimental.

Preserve the approved text: “Helping elders live well and live longer.”
The Sunny link is https://mysunny.world/. Keep this website simple.

Use branch → PR → CI → independent review → merge → deploy → hosted evidence.
Do not publish any strategy notes, account screenshots, credentials, or other
private source material. Never receive, store, print, or log private key material.

Commands:

- Install: `npm ci`
- Format: `npm run format` (also run on save before committing)
- Format check: `npm run format:check`
- Lint and static analysis: `npm run lint` (HTML Validate recommended and CSS-tree property grammar validation)
- Type checking: no typed source; strict HTML/CSS validation is the applicable static check.
- Tests: `npm test`
- Build: `npm run build`
- Preview: `python3 -m http.server 8769 --directory site`

Architecture: `site` contains exactly three public files. `scripts/build.py`
packages only those files and .nojekyll. The custom domain is configured in GitHub
Pages settings; Actions publishing does not use a CNAME file. There are no runtime
secrets or dependencies. Development dependencies are locked in package-lock.json.
