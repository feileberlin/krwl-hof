# ⚠️ GitHub Wiki Needs One-Time Initialization

## Quick Summary

The documentation is ready and will automatically sync to the GitHub Wiki, but the Wiki needs to be initialized first (one-time step).

## What's Happening

✅ **Documentation is ready**: All files are in `docs/` directory and work perfectly as standalone markdown  
✅ **Automated sync is configured**: Workflow `.github/workflows/docs.yml` will sync on every push to `main`  
✅ **Wiki feature is enabled**: Repository settings show `"has_wiki": true`  
❌ **Wiki repository doesn't exist yet**: Needs manual initialization

## Solution (Repository Owner Only)

### Option 1: Initialize via GitHub UI (Simplest - 30 seconds)

1. Visit https://github.com/feileberlin/krwl-hof/wiki
2. Click **"Create the first page"**
3. Enter any title (e.g., "Home")
4. Enter any content (e.g., "Initializing...")
5. Click **"Save Page"**

Done! The Wiki repository now exists. The automated workflow will replace this placeholder with real documentation on the next push to `main`.

### Option 2: Trigger Immediate Sync (After Option 1)

If you want the documentation to appear immediately:

1. Go to https://github.com/feileberlin/krwl-hof/actions/workflows/docs.yml
2. Click **"Run workflow"**
3. Select branch: `main`
4. Ensure **"Sync documentation to GitHub Wiki"** is `true`
5. Click **"Run workflow"**

The workflow will sync all documentation files to the Wiki within a minute.

### Option 3: Manual Sync Script (For advanced users)

```bash
# From repository root
./sync-to-wiki.sh

# Then push to wiki:
cd /tmp/krwl-hof.wiki
git add .
git commit -m 'Initial documentation sync'
git push
```

## Why This Happens

GitHub Wiki is a **separate Git repository** (`feileberlin/krwl-hof.wiki.git`). Until someone creates the first page through GitHub's UI, this repository doesn't exist. Once it exists, automated workflows can push to it.

This is standard GitHub behavior and affects all repositories using automated Wiki sync.

## What Gets Synced

Once initialized, these files will automatically appear in the Wiki:

- **docs/Home.md** → Wiki home page
- **docs/_Sidebar.md** → Wiki sidebar navigation
- **docs/_Footer.md** → Wiki footer
- **docs/SETUP.md** → Setup guide
- **docs/SCRAPING.md** → Scraping guide
- **docs/DEPLOYMENT.md** → Deployment guide
- **docs/LEAFLET_I18N.md** → i18n guide
- **docs/WIKI_SETUP.md** → Wiki setup guide (this document)
- **TESTING.md** → Testing guide
- **static/LOCALIZATION.md** → Static-LOCALIZATION.md (App localization)
- **static/PWA_README.md** → Static-PWA.md (PWA features)
- **.github/DEV_ENVIRONMENT.md** → Dev-Environment.md
- **.github/FEATURE_REGISTRY.md** → Dev-Feature-Registry.md
- **.github/DEPLOYMENT.md** → Dev-Deployment.md
- **.github/PROMOTE_WORKFLOW.md** → Dev-Promote-Workflow.md

> **Note**: GitHub Wiki requires flat structure. Files from subdirectories are copied with prefixes.

## Verification

After initialization and sync:

1. Visit https://github.com/feileberlin/krwl-hof/wiki
2. You should see the Home page with full documentation
3. Sidebar should show navigation menu
4. Footer should show community info

## Documentation Still Works Without Wiki!

**Important**: The documentation works perfectly as standalone markdown files in the `docs/` directory. The Wiki is just an additional convenient way to browse it. Contributors and developers can use the docs without waiting for Wiki initialization.

## More Details

See **[docs/WIKI_SETUP.md](docs/WIKI_SETUP.md)** for comprehensive setup guide, troubleshooting, and technical details.

## Summary

**Repository Owner**: Visit the Wiki tab, click "Create the first page", save. Done! 🚀  
**Everyone Else**: Documentation works perfectly in `docs/` directory right now. No action needed.
