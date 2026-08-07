# Publications Migration Checklist

Goal: move the full publications catalog to the resume website, and slim this
repository (and its docs site) down to the dissertation only, with a link out
to the resume site for the rest of the research.

Directory of record: `docs/publications/` (~28 MB). It is self-contained.
The rendered page `docs/publications/index.md` is generated from
`docs/publications/publications.bib` by
`scripts/generate_docs.py::generate_publications_page()`.

---

## Part A -- Copy publications to the resume site

- [ ] Copy the entire `docs/publications/` folder into the resume repo.
- [ ] Treat `publications.bib` as the source of truth. If the resume site has
      its own rendering, wire it to this `.bib` and drop the generated
      `index.md`. If not, keep `index.md` as the pre-rendered page.
- [ ] Bring over the 19 dated folders with their PDFs and notebooks (the 28 MB
      of downloadable artifacts). Confirm every PDF referenced by an entry made
      the trip.
- [ ] Decide how large binaries are stored on the resume site (plain git,
      Git LFS, or an external asset host). 28 MB of PDFs may warrant LFS.
- [ ] Verify every entry renders and every download link resolves on the
      resume site before removing anything here.
- [ ] Note the public URL of the resume publications page -- you will link to
      it from this repo in Part B.

## Part B -- Reduce this repo to the dissertation only

- [ ] Remove the publications catalog from the docs site nav: delete the
      `- Publications/: publications` line in `docs/.pages.yml`.
- [ ] Replace the Publications section on the landing page
      (`docs/index.md`, ~lines 88-90) so `[View Publications]` points to the
      resume site URL instead of `publications/`.
- [ ] Retire the generator: remove the `generate_publications_page()` call in
      `scripts/generate_docs.py::main()` (and optionally the function,
      `PUB_DIR`/`PUB_INDEX` constants, `parse_bibtex`, `find_pdfs_for_entry`,
      and `MONTH_MAP` if unused elsewhere).
- [ ] Delete the `docs/publications/` directory from this repo once Part A is
      verified. (Optional: keep only `publications.bib` if the dissertation
      still cites it; otherwise remove it too.)
- [ ] Search for and update any other references to publications:
      run `grep -rin "publication" docs/ scripts/ mkdocs.yml README.md`
      and fix stragglers.
- [ ] Update `CLAUDE.md`: remove the publications rows from the docs data-flow
      and `.pages.yml` hierarchy tables (`publications.bib -> index.md`,
      `docs/publications/.pages.yml`).
- [ ] Add a short "Other research & publications" pointer in `README.md` and/or
      the docs landing page linking to the resume site.

## Part C -- Verify and ship

- [ ] Run `make docs` and confirm a clean build with no broken links and no
      dangling Publications nav entry.
- [ ] Serve locally (`make docs-serve`) and click through Home + nav to confirm
      the resume-site link works and nothing 404s.
- [ ] Confirm `git status` shows the `docs/publications/` removal and the size
      of the repo dropped accordingly.
- [ ] Commit on the feature branch and push.
- [ ] Merge to `main` to trigger the CI docs deploy
      (`.github/workflows/ci.yml`); confirm the live site at
      https://ryan-a-bell.github.io/dissertation/ no longer lists publications
      and links out correctly.

## Notes / decisions to make

- [ ] Redirect vs. removal: decide whether the old `/publications/` URL on the
      docs site should 404, redirect to the resume site, or show a stub page
      that links out. (A stub `docs/publications/index.md` with just a link is
      the lowest-risk option for existing inbound links.)
- [ ] Scope call: several entries are broader than the dissertation
      (cost modeling, MBSE, VQA, Delphi). Confirm all of them move to the
      resume site and none need to stay behind as dissertation citations.
