# flashcards
## Flashcard viewer

Every `.md` file in the repo (except this README) is turned into flashcards.
Each `**Question:**` line starts a card, and the lines under it are the answer.
Images on their own line (`![](fi/...)`) appear on the answer side of the card above them.

Build locally:

    python3 build.py      # writes _site/index.html; open it in a browser

Publishing with GitHub Pages: a workflow in `.github/workflows/pages.yml` builds and
deploys the site on every push to `main`. One-time setup: in the repo go to
Settings → Pages → Build and deployment → Source, and choose **GitHub Actions**.

Editing cards in the browser: tap **Edit card** or **+ Add card**. Editing needs a
GitHub token, set once under **Settings**:

1. On GitHub, create a fine-grained personal access token (Settings → Developer
   settings → Fine-grained tokens). Restrict it to this repository and give it
   **Contents: Read and write**.
2. In the viewer, open Settings and paste the token.

Saving commits the change to the `.md` file in the repo. The Pages workflow then
rebuilds the site, usually within a minute or two. The token is stored only in
the browser you enter it in; use **Forget token** on shared devices.

Marks are stored per browser. Use **Export marks** to save them as a JSON file and
**Import marks** on another device to merge them in.
