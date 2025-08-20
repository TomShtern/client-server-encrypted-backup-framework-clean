# KivyMD GUI Fix Plan

## Critical Issues Identified

### 1. Missing/Broken Import Components
- `MDTextFieldSupportingText` - Does not exist in current KivyMD version
- `MDFloatingActionButton` - Import path incorrect
- Legacy import paths from KivyMD 1.x still being used

### 2. Installation Issues
- Current KivyMD installation appears incomplete or corrupted
- Need to reinstall with specific stable commit as per CLAUDE.md

## Immediate Fix Strategy

### Phase 1: Environment Recovery (CRITICAL - Do First)
```bash
# 1. Activate correct virtual environment
.\kivy_venv_new\Scripts\activate

# 2. Clean reinstall KivyMD with stable commit
pip uninstall kivymd -y
pip install git+https://github.com/kivymd/KivyMD.git@d2f7740

# 3. Verify psutil dependency
pip install psutil==7.0.0
```

### Phase 2: Import Path Corrections
**Priority Files to Fix:**
1. `kivymd_gui/screens/files.py` - `MDFloatingActionButton` import
2. `kivymd_gui/main.py` - Core app imports  
3. All screen files with text field components

**Key Import Fixes Needed:**
```python
# ❌ REMOVE: These don't exist
from kivymd.uix.textfield import MDTextFieldSupportingText

# ✅ REPLACE WITH: Component-based approach
from kivymd.uix.textfield import MDTextField
# Supporting text is now a child component

# ❌ REMOVE: Wrong path
from kivymd.uix.floatingactionbutton import MDFloatingActionButton

# ✅ REPLACE WITH: Correct path
from kivymd.uix.floatingactionbutton import MDFloatingActionButton
# OR check if it's in kivymd.uix.button now
```

### Phase 3: Component Architecture Updates
**Convert to KivyMD 2.0.x Component-Based Design:**

1. **MDTextField with Supporting Text:**
```python
# OLD (doesn't work):
MDTextField(helper_text="Enter port")

# NEW (component-based):
MDTextField(
    MDTextFieldSupportingText(text="Enter port"),
    mode="outlined"
)
```

2. **MDTopAppBar Updates:**
```python
# OLD:
MDTopAppBar(title="Dashboard")

# NEW:
MDTopAppBar(
    MDTopAppBarTitle(text="Dashboard"),
    type="small"
)
```

### Phase 4: Critical Functionality Fixes

#### A. Navigation System
- Ensure MDNavigationRail works with new component structure
- Fix navigation callbacks and screen switching

#### B. Data Tables & Lists  
- Update MDDataTable imports and usage
- Fix list item components if broken

#### C. Dialogs & Popups
- Verify dialog components work with new API
- Fix any popup/snackbar issues

## Testing Strategy

### 1. Incremental Testing
```bash
# Test after each phase
python kivymd_gui/main.py

# Look for specific error patterns:
# - ImportError: Check import fixes
# - AttributeError: Check component structure
# - Runtime errors: Check event bindings
```

### 2. Component Verification
- Dashboard screen loads without errors
- Navigation between screens works
- Basic server status display functions
- Text fields accept input properly

## Emergency Rollback Plan

If fixes break more functionality:
```bash
# 1. Revert to working state
git checkout -- kivymd_gui/

# 2. Try alternative KivyMD version
pip install kivymd==1.1.1  # Known stable version

# 3. Simplify components to basic Kivy if needed
# Replace complex KivyMD components with basic Kivy equivalents
```

## Success Criteria

✅ **Minimum Viable GUI:**
- Application starts without import errors
- Main dashboard displays
- Basic navigation works
- Can view server status

✅ **Full Functionality:**
- All screens accessible
- Server management controls work
- File transfer monitoring displays
- Settings persistence works

## Implementation Order

1. **CRITICAL FIRST:** Fix environment and KivyMD installation
2. **HIGH:** Fix import errors preventing startup
3. **MEDIUM:** Update component structure for compatibility  
4. **LOW:** Enhance UI/UX after basic functionality works

## Notes

- Keep CLAUDE.md patterns as reference for KivyMD 2.0.x syntax
- Test frequently - don't batch too many changes
- Focus on getting basic functionality first, then enhance
- Document any new component patterns discovered during fixes