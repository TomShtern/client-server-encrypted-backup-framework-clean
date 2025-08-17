# CircleCI Quick Setup Checklist
**Step-by-step setup for your Encrypted Backup Framework**

## Pre-Setup (5 minutes)

### ✅ Cost Awareness
- [ ] **Budget**: CircleCI Windows builds cost ~$0.40/minute
- [ ] **Estimated monthly cost**: $50-200+ depending on usage
- [ ] **Free tier**: Limited Windows build minutes
- [ ] **Alternative considered**: GitHub Actions (cheaper for Windows)

### ✅ Repository Preparation
- [ ] All files are committed and pushed to GitHub
- [ ] `.circleci/config.yml` is in your repository
- [ ] `requirements.txt` is up to date
- [ ] `vcpkg.json` contains all C++ dependencies

## Setup Steps (15 minutes)

### Step 1: CircleCI Account Setup
- [ ] Go to [circleci.com](https://circleci.com)
- [ ] Sign up with your GitHub account
- [ ] Authorize CircleCI to access your repositories

### Step 2: Project Connection
- [ ] Click "Set Up Project" next to your repository name
- [ ] Choose "Use Existing Config" (we created `.circleci/config.yml`)
- [ ] Click "Start Building"
- [ ] **First build will likely fail** - this is normal!

### Step 3: Environment Variables
In CircleCI Project Settings → Environment Variables, add:

**Required**:
- [ ] `PYTHONIOENCODING` = `utf-8`
- [ ] `PYTHONUTF8` = `1`

**Optional**:
- [ ] `SENTRY_DSN` = `your_sentry_dsn_here`
- [ ] `LOG_LEVEL` = `INFO`

### Step 4: GitHub Integration
- [ ] Go to GitHub repository → Settings → Branches
- [ ] Add branch protection rule for `main`/`clean-main`
- [ ] Require status checks: ✅ `ci/circleci: python-lint-and-deps`
- [ ] Require status checks: ✅ `ci/circleci: integration-tests`

### Step 5: First Build Monitoring
- [ ] Watch the first build in CircleCI dashboard
- [ ] **Expected duration**: 30-45 minutes (vcpkg build)
- [ ] **Expected result**: Some tests may fail initially

## Troubleshooting First Build (Common Issues)

### ❌ vcpkg Build Fails
**Symptoms**: C++ build fails with dependency errors
**Solution**:
```bash
# Check vcpkg.json has all dependencies
{
  "dependencies": [
    "cryptopp",
    "boost",
    "zlib", 
    "sentry-native"
  ]
}
```

### ❌ Python Import Errors
**Symptoms**: `ModuleNotFoundError` in Python tests
**Solution**:
```bash
# Update requirements.txt with missing packages
pip freeze > requirements.txt
```

### ❌ UTF-8 Encoding Errors
**Symptoms**: Unicode decoding errors
**Solution**: Verify environment variables are set (Step 3)

### ❌ Port Conflicts
**Symptoms**: Integration tests fail with "port in use"
**Solution**: Tests will retry automatically, monitor build logs

### ❌ Build Timeout
**Symptoms**: Build exceeds time limit
**Solution**: Increase timeout in CircleCI settings or optimize build

## Post-Setup Configuration (10 minutes)

### Notifications
- [ ] CircleCI → Project Settings → Notifications
- [ ] Enable email notifications for failed builds
- [ ] Add Slack integration (optional)

### Cost Monitoring
- [ ] CircleCI → Plan → Usage
- [ ] Set up billing alerts
- [ ] Monitor Windows build minute consumption

### Build Optimization
- [ ] Monitor first few builds for performance
- [ ] Enable caching if builds are slow (documented in config)
- [ ] Consider GitHub Actions if costs are too high

## Validation Checklist (After First Successful Build)

### ✅ All Pipelines Working
- [ ] Python linting passes
- [ ] C++ build completes successfully
- [ ] Security scans run without critical issues  
- [ ] Integration tests pass (or show expected failures)

### ✅ GitHub Integration
- [ ] Pull requests show CircleCI status checks
- [ ] Protected branches block merges on failed builds
- [ ] Build status badge shows on repository (optional)

### ✅ Team Workflow
- [ ] Team members understand build process
- [ ] Failure notification process established
- [ ] Build costs are acceptable

## Success Indicators

### 🎯 Green Build
Your build is successful when you see:
- ✅ Python dependencies installed
- ✅ C++ client compiled (`EncryptedBackupClient.exe` created)
- ✅ Security scans completed
- ✅ Integration tests pass (or fail with known issues)

### 📊 Performance Metrics
Track these for ongoing success:
- **Build duration**: <45 minutes
- **Success rate**: >90%
- **Monthly cost**: Within budget
- **Team adoption**: Regular use by developers

## Alternative: GitHub Actions Setup

If CircleCI costs are too high, consider GitHub Actions:

### Pros
- **Cheaper**: ~$0.08/minute for Windows (vs $0.40/minute)
- **Better GitHub integration**
- **Generous free tier**

### Quick Alternative Setup
1. Create `.github/workflows/ci.yml` instead of `.circleci/config.yml`
2. Use `actions/setup-python@v4` and `microsoft/setup-msbuild@v1`
3. Follow similar job structure as CircleCI config

## Emergency Contacts & Resources

### If Things Go Wrong
- **CircleCI Support**: [support.circleci.com](https://support.circleci.com)
- **Documentation**: [circleci.com/docs](https://circleci.com/docs)
- **Community**: [discuss.circleci.com](https://discuss.circleci.com)

### Quick Commands
```bash
# Local config validation
circleci config validate

# Force rebuild
git commit --allow-empty -m "Trigger rebuild"
git push

# Check build status
# Visit: https://app.circleci.com/pipelines/github/yourusername/your-repo
```

## Final Notes

### Expected Timeline
- **Setup**: 30 minutes
- **First successful build**: 1-2 hours (including troubleshooting)
- **Team onboarding**: 1 week
- **Full optimization**: 2-4 weeks

### Investment vs. Return
- **Setup cost**: 2-4 hours of developer time
- **Monthly cost**: $50-200 in build minutes
- **Benefit**: Automated testing, early bug detection, deployment automation
- **ROI**: Usually positive within first month for active projects

---

**🚀 Ready to Start?** 
Begin with Step 1 above and work through the checklist. Remember: the first build will likely have issues - this is completely normal for complex projects!