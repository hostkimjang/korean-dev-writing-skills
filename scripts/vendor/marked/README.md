# Marked 17.0.5

Vendored from the published `marked@17.0.5` npm package. The ESM distribution
`lib/marked.esm.js` is stored as `marked.esm.mjs` so Node can load it without
a repository-wide package manifest or dependency installation. Its bytes are unchanged.

- Upstream: https://github.com/markedjs/marked
- Package: https://www.npmjs.com/package/marked/v/17.0.5
- License: MIT; see [LICENSE.md](LICENSE.md).
- Distribution SHA-256: `0b4487359ce6b85108708e7a532e1242a27f4718241e7b2de109ac6cd307d2dc`
- Requires Node.js 20 or newer.

To update, replace the distribution and license together, update this provenance,
and run the viewer freshness and functional checks documented in the repository.
The trailing source-map reference is unused by the Node build; no network access
is needed to render Markdown.
