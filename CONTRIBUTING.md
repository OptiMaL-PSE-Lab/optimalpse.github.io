# Adding or updating your profile

You can add or edit your profile on the People page yourself, all in the
browser. You only need a free GitHub account. You never need to install
anything.

When you're done, you open a **pull request**. Website admins review and merge it, and your profile
goes live a few minutes later.

---

## I'm new: create my profile

### Step 1: Prepare your files

You need two things:

1. **Your profile text.** Open the
   [profile template](https://github.com/OptiMaL-PSE-Lab/optimalpse.github.io/blob/main/profile-template/_index.md),
   click the **copy** button (top right of the file), and paste it into a text
   editor. Fill in your details. The comments (lines starting with `#`) explain
   each field.
2. **A photo** named `avatar.jpg` (or `avatar.png`). It should be a roughly
   square headshot. It will be cropped into a circle. Keep it under 10 MB.

> ⚠️ The photo must be a *real* JPG or PNG. Photos from iPhones (HEIC) or saved
> from websites (WebP) won't work just by renaming them. Open the photo and use
> **Export / Save As → JPEG** instead.

Pick a **username**: your first name in lowercase, e.g. `jane`. If that's
taken (check [content/authors](https://github.com/OptiMaL-PSE-Lab/optimalpse.github.io/tree/main/content/authors)),
add your surname: `jane-doe`. Put it in the `authors:` field of your profile.

### Step 2: Upload them

**Easiest: upload a folder**

1. On your computer, make a folder named after your username (e.g. `jane`).
   Save your profile text inside it as `_index.md` and put your `avatar.jpg`
   next to it.
2. Go to
   [**upload to content/authors**](https://github.com/OptiMaL-PSE-Lab/optimalpse.github.io/upload/main/content/authors).
3. **Drag the whole folder** onto the page. GitHub keeps the folder structure.
4. Scroll down, write a short message like "Add Jane Doe profile", and click
   **Propose changes**, then **Create pull request**.

**Alternative: type it in the browser**

1. Go to
   [**new file in content/authors**](https://github.com/OptiMaL-PSE-Lab/optimalpse.github.io/new/main/content/authors).
2. In the file name box type `jane/_index.md`. Typing the `/` creates the folder.
3. Paste your filled-in profile, then click **Propose changes** →
   **Create pull request**.
4. Add your photo to the same pull request: on the pull request page, click
   the branch name under the title (e.g. `yourname:patch-1`), go to
   `content/authors/jane/`, click **Add file → Upload files**, drop in
   `avatar.jpg`, and choose **Commit directly to the `patch-1` branch**.

---

## I already have a profile: update it

1. Find your folder in
   [content/authors](https://github.com/OptiMaL-PSE-Lab/optimalpse.github.io/tree/main/content/authors)
   and open `_index.md`.
2. Click the ✏️ **pencil** icon (top right), make your changes, then
   **Propose changes** → **Create pull request**.
3. To change your photo: in your folder, click **Add file → Upload files**
   and upload a new `avatar.jpg`. It replaces the old one.

Common updates:

- **Moving on?** Change `user_groups` to `Alumni` and update `role`.
- **New links?** Add or remove entries under `social:`.

---

## After you open the pull request

An automatic check runs on your pull request. If it shows a red ❌, click
**Details** to see what's wrong. Common problems are a misspelled
`user_groups` value, an `authors:` username that doesn't match the folder
name, or a photo that isn't really a JPG/PNG. Fix the file the same way you
edited it, and the check reruns automatically.

Once it's green ✅, a website admin will merge it.

## Previewing locally (optional)

If you have [Hugo](https://gohugo.io/installation/) installed, you can run
`hugo server` in the repository and open <http://localhost:1313/people/>.
