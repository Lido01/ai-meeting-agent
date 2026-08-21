# 🤝 Contribution Guidelines

To maintain a clean project history and avoid overwriting each other's work, please follow this strict workflow. Direct commits to `main` or `dev` are strictly blocked.

## 🚀 The Development Workflow

### 1. Create a Feature Branch
Never work directly on `dev`. Always branch off from `dev` to do your work:
```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### 2. Commit and Push Your Work
Keep your commits descriptive. Push your feature branch to the remote server:
```bash
git add .
git commit -m "feat: add user authentication layout"
git push origin feature/your-feature-name
```

### 3. Open a Pull Request (PR)
* Open your browser and navigate to the repository.
* Open a PR targeting the **`dev`** branch (NOT `main`).
* Wait for a team member to review the code and approve the merge.

### 4. Clean Up Locally
Once your PR is successfully merged on the server, clean up your local computer:
```bash
git checkout dev
git pull origin dev
git branch -d feature/your-feature-name
```


<!-- PULL_REQUEST_TEMPLATE -->
## 📝 Description
Provide a brief summary of the changes introduced by this PR.

## ⚙️ Branch Check (Mandatory)
- [ ] My PR targets the **`dev`** branch (Not `main`).
- [ ] I verified that this branch does not include accidental commits from other branches.

## 🧪 Testing
- [ ] I have tested these changes locally, and the project builds successfully.
- [ ] No TypeScript or linting errors are present.
