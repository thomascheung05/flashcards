# flashcards
## Flashcard viewer

Each course lives in its own folder, with its `.md` file(s) and an `fi/` folder for its images:

    HENVPaus/
        HENVPaus FlashCards.md
        fi/p02_001.png
    Another Course/
        Another Course.md
        fi/...

Every folder that contains a `.md` file becomes a course tab at the top of the site.
Each `**Question:**` line starts a card, and the lines under it are the answer.
Images on their own line (`![](fi/...)`) appear on the answer side of the card above them.
The path is relative to the course folder, so keep the `fi/` folder inside it.
The site remembers the last course you opened on this device.

Build locally:

    python3 build.py      # writes _site/index.html; open it in a browser

Publishing with GitHub Pages: a workflow in `.github/workflows/pages.yml` builds and
deploys the site on every push to `main`. One-time setup: in the repo go to
Settings → Pages → Build and deployment → Source, and choose **GitHub Actions**.

To change cards, edit the `.md` file and push. The Pages workflow rebuilds the site, usually within a minute or two.

Marks are stored per browser. The ☾ Dark / ☀ Light button switches the theme and remembers the choice; until you pick one, it follows your device setting. Use **Export marks** to save them as a JSON file and
**Import marks** on another device to merge them in.
