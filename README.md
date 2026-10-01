# ANTZ Home Page Redesign: finalized review build

The exact files behind **<https://home-page-redesign-gold.vercel.app/?v=2>**, frozen on 1 October 2026.

```bash
git clone --branch Handoff --single-branch https://github.com/naveen-lset/Module_Selection-Home-page-.git antz-home-handoff
cd antz-home-handoff
python3 -m http.server 8080   # then open http://localhost:8080/
```

No install and no build: it's a static site, so any file server works. It must be served over HTTP, not opened as a file. On localhost the console shows one harmless 404 for an internal dev toolbar; see HANDOFF.md §1.

**Read [HANDOFF.md](HANDOFF.md)** before building on it. It covers each screen, the design rules, the data, the known gaps and a QA checklist.

The app is developed on branch `site-command-centre`; this build comes from commit `2a73a0e`.
