# 🌳 Branching Strategy - Surface Cutting Optimizer

Professional Git branching model for library development and maintenance.

## 📋 Branch Structure Overview

Our project follows a **Git Flow** inspired branching strategy optimized for library development and continuous integration.

## 🎯 Main Branches

### 1. **`main`** - Production Branch
- **Purpose:** Stable, production-ready releases
- **Protection:** ✅ Protected, requires PR reviews
- **Merges from:** `release/*` and `hotfix/*` branches only
- **Auto-deploy:** 🚀 Triggers PyPI release on tag
- **Status:** Always deployable

### 2. **`develop`** - Integration Branch  
- **Purpose:** Integration of completed features
- **Protection:** ✅ Protected, requires PR reviews
- **Merges from:** `feature/*` branches
- **Merges to:** `release/*` branches
- **Status:** Latest development state

## 🔧 Supporting Branches

### Feature Branches: `feature/*`

#### **`feature/technical-demos`** 
- **Current Work:** ✅ Professional technical demonstrations
- **Includes:** Industry-specific demos, algorithm showcases
- **Status:** Ready for review and merge to develop

#### **`feature/algorithm-improvements`**
- **Purpose:** Algorithm optimization and new implementations
- **Examples:** Performance tuning, new cutting algorithms
- **Merges to:** `develop`

#### **`feature/performance-optimization`**
- **Purpose:** Speed and memory optimizations
- **Examples:** Caching, parallel processing, memory management
- **Merges to:** `develop`

#### **`feature/documentation-update`**
- **Purpose:** Documentation improvements and API docs
- **Examples:** README updates, code documentation, tutorials
- **Merges to:** `develop`

#### **`feature/testing-improvements`**
- **Purpose:** Test coverage and quality improvements
- **Examples:** Unit tests, integration tests, performance benchmarks
- **Merges to:** `develop`

### Release Branches: `release/*`

#### **`release/v1.0.0`**
- **Purpose:** Prepare version 1.0.0 for production
- **Activities:** Bug fixes, version updates, final testing
- **Merges to:** `main` and `develop`

### Hotfix Branches: `hotfix/*`

#### **`hotfix/critical-fixes`**
- **Purpose:** Critical production fixes
- **Creates from:** `main`
- **Merges to:** `main` and `develop`

---

## 🔄 Workflow Processes

### 1. **Feature Development**
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/new-feature-name

# Work on feature
git add .
git commit -m "feat: implement new feature"

# Push and create PR
git push origin feature/new-feature-name
# Create PR: feature/new-feature-name → develop
```

### 2. **Release Process**
```bash
# Create release branch
git checkout develop
git checkout -b release/v1.1.0

# Final preparations
git commit -m "chore: bump version to 1.1.0"

# Merge to main
git checkout main
git merge release/v1.1.0
git tag v1.1.0

# Merge back to develop
git checkout develop
git merge release/v1.1.0
```

### 3. **Hotfix Process**
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Fix and commit
git commit -m "fix: resolve critical production bug"

# Merge to main
git checkout main
git merge hotfix/critical-bug-fix
git tag v1.0.1

# Merge to develop
git checkout develop
git merge hotfix/critical-bug-fix
```

---

## 📊 Branch Protection Rules

### **Main Branch Protection**
- ✅ Require pull request reviews (2 reviewers)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators
- ✅ Allow force pushes: ❌

### **Develop Branch Protection**
- ✅ Require pull request reviews (1 reviewer)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Allow force pushes: ❌

### **Required Status Checks**
- ✅ Unit Tests (Python 3.8, 3.9, 3.10, 3.11)
- ✅ Integration Tests
- ✅ Performance Tests
- ✅ Code Quality (Black, Flake8, MyPy)
- ✅ Documentation Build

---

## 🎯 Commit Message Convention

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **style:** Code style changes (formatting, etc.)
- **refactor:** Code refactoring
- **perf:** Performance improvements
- **test:** Test changes
- **chore:** Build process or auxiliary tool changes

### Examples
```bash
feat(algorithms): add hybrid genetic algorithm implementation
fix(geometry): resolve circle placement overlap detection
docs(readme): update installation instructions
test(integration): add algorithm performance benchmarks
refactor(core): transform cost-focused approach to technical focus
```

---

## 🚀 Release Strategy

### Version Numbering
- **MAJOR.MINOR.PATCH** (Semantic Versioning)
- **Major:** Breaking changes
- **Minor:** New features, backward compatible
- **Patch:** Bug fixes, backward compatible

### Release Types

#### **Alpha Releases** (`v1.0.0-alpha.1`)
- Early development versions
- Internal testing only
- May have incomplete features

#### **Beta Releases** (`v1.0.0-beta.1`)
- Feature complete
- External testing
- API may change slightly

#### **Release Candidates** (`v1.0.0-rc.1`)
- Production ready candidates
- Final testing
- No new features

#### **Stable Releases** (`v1.0.0`)
- Production ready
- Full documentation
- PyPI distribution

---

## 📁 Current Branch Status

| Branch | Status | Purpose | Next Action |
|--------|--------|---------|-------------|
| `main` | ✅ Stable | Production releases | Ready for v1.0.0 |
| `develop` | 🔄 Active | Integration | Merge features |
| `feature/technical-demos` | ✅ Ready | Professional demos | **Ready for PR** |
| `feature/algorithm-improvements` | 🆕 New | Algorithm optimization | Available for development |
| `feature/performance-optimization` | 🆕 New | Performance tuning | Available for development |
| `feature/documentation-update` | 🆕 New | Documentation | Available for development |
| `feature/testing-improvements` | 🆕 New | Test improvements | Available for development |
| `release/v1.0.0` | 🆕 New | Release preparation | Available for release prep |
| `hotfix/critical-fixes` | 🆕 New | Production fixes | Available for hotfixes |

---

## 💡 Best Practices

### **Branch Naming**
- Use lowercase with hyphens
- Be descriptive but concise
- Include issue number when applicable
- Examples: `feature/add-laser-cutting-demo`, `fix/geometry-overlap-bug`

### **Pull Requests**
- Clear, descriptive titles
- Detailed descriptions with context
- Reference related issues
- Include testing evidence
- Request appropriate reviewers

### **Code Reviews**
- Focus on code quality and maintainability
- Check test coverage
- Verify documentation updates
- Ensure consistent coding style
- Test locally when possible

### **Merging Strategy**
- Use **"Squash and merge"** for feature branches
- Use **"Create a merge commit"** for release branches
- Delete feature branches after merge
- Keep commit history clean and meaningful

---

## 🔧 Setup Commands

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd surface-cutting-optimizer

# Set up development environment
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Working with Branches
```bash
# List all branches
git branch -a

# Create and switch to new feature branch
git checkout -b feature/my-new-feature

# Push new branch to origin
git push -u origin feature/my-new-feature

# Sync with latest develop
git fetch origin
git checkout develop
git pull origin develop
```

This branching strategy ensures **code quality**, **collaborative development**, and **reliable releases** for the Surface Cutting Optimizer library. 🚀 