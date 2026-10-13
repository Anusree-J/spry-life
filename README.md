# Spry Life

Helping elders live well and live longer.

The public company website at https://sprylife.org, hosted on GitHub Pages.

- Preview: `python3 -m http.server 8769 --directory site`
- Install development checks: `npm ci`
- Format: `npm run format`
- Check: `npm run format:check && npm run lint && npm test`
- Build: `npm run build`

Changes go through a pull request and review. After checks pass and the PR is
merged, GitHub Actions publishes only `dist` to Pages. No runtime dependencies,
JavaScript, forms, analytics, or secrets. Roll back by reverting the release PR
and letting the same checks and deployment workflow run.
