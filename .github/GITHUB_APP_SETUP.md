# GitHub App Setup for Semantic Release

This guide walks through creating a GitHub App to enable semantic-release to bypass branch protection rules securely.

## Why Use a GitHub App?

- ✅ Most secure authentication method (scoped permissions, short-lived tokens)
- ✅ Can bypass repository rulesets when added to bypass list
- ✅ Triggers downstream workflows (unlike GITHUB_TOKEN)
- ✅ Auditable in GitHub's audit log
- ✅ Recommended by GitHub as of 2025

## Step 1: Create the GitHub App

1. **Navigate to GitHub App Settings**
   - Go to <https://github.com/settings/apps>
   - Click **"New GitHub App"**

2. **Configure Basic Information**
   - **GitHub App name**: `peakbagger-release-bot` (or any unique name)
   - **Description**: `Automated release bot for peakbagger-cli using semantic-release`
   - **Homepage URL**: `https://github.com/dreamiurg/peakbagger-cli`
   - **Webhook**: Uncheck **"Active"** (we don't need webhooks)

3. **Set Repository Permissions**

   Under "Repository permissions", set these permissions:

   | Permission | Access Level | Purpose |
   |------------|-------------|---------|
   | **Contents** | Read and write | Push commits, create tags |
   | **Issues** | Read and write | Comment on issues in releases |
   | **Pull requests** | Read and write | Comment on PRs in releases |
   | **Metadata** | Read-only | Required (auto-selected) |

4. **Configure Installation**
   - Under "Where can this GitHub App be installed?"
   - Select: **"Only on this account"**

5. **Create the App**
   - Click **"Create GitHub App"**
   - You'll be redirected to the app's settings page

## Step 2: Generate Private Key

1. On your app's settings page, scroll to **"Private keys"**
2. Click **"Generate a private key"**
3. A `.pem` file will download automatically
4. **IMPORTANT**: Save this file securely - you'll need it in Step 4

## Step 3: Note the App ID

1. At the top of the app settings page, find **"App ID"**
2. Copy this number (e.g., `123456`)
3. Save it for Step 4

## Step 4: Install the App on Your Repository

1. On your app's settings page, click **"Install App"** in the left sidebar
2. Click **"Install"** next to your username/organization
3. Select: **"Only select repositories"**
4. Choose: `peakbagger-cli`
5. Click **"Install"**

## Step 5: Add Repository Secrets

1. **Go to repository secrets**
   - Navigate to <https://github.com/dreamiurg/peakbagger-cli/settings/secrets/actions>
   - Click **"New repository secret"**

2. **Add App ID**
   - Name: `RELEASE_APP_ID`
   - Value: The App ID from Step 3 (e.g., `123456`)
   - Click **"Add secret"**

3. **Add Private Key**
   - Click **"New repository secret"** again
   - Name: `RELEASE_APP_PRIVATE_KEY`
   - Value: Open the `.pem` file from Step 2 and paste the **entire contents** including:

     ```text
     -----BEGIN RSA PRIVATE KEY-----
     ... (your key content) ...
     -----END RSA PRIVATE KEY-----
     ```

   - Click **"Add secret"**

## Step 6: Add App to Ruleset Bypass List

1. **Navigate to Repository Rules**
   - Go to <https://github.com/dreamiurg/peakbagger-cli/settings/rules>
   - Click on the **"main"** ruleset

2. **Add Bypass Actor**
   - Scroll to **"Bypass list"**
   - Click **"Add bypass"**
   - Select **"Apps"**
   - Find and select your app: `peakbagger-release-bot`
   - Bypass mode: **"Always allow"**
   - Click **"Save changes"**

## Step 7: Verify Configuration

After merging the workflow PR, the release workflow will:

1. Generate a short-lived token from your GitHub App
2. Use that token to checkout and push to the repository
3. Bypass the ruleset rules because the app is in the bypass list
4. Create releases, update changelog, and bump versions automatically

## Troubleshooting

### "App not found in bypass list"

- Make sure you installed the app on the repository (Step 4)
- Verify the app appears in Settings → Integrations → GitHub Apps

### "Invalid private key"

- Ensure you copied the entire `.pem` file including header/footer
- Check for no extra spaces or newlines

### "Insufficient permissions"

- Review Step 3 and ensure all required permissions are granted
- You may need to update permissions in the app settings

## Security Notes

- **Private key**: Never commit the `.pem` file to version control
- **Token lifetime**: App tokens expire after 1 hour (much safer than PATs)
- **Scope**: The app only has access to repositories where it's installed
- **Rotation**: Regenerate private keys periodically for security

## References

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Repository Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [actions/create-github-app-token](https://github.com/actions/create-github-app-token)
