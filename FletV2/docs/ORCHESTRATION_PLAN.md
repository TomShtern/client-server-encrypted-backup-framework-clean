# FletV2 Consolidation Plan Orchestration Strategy

## Overview

This document outlines how to divide the work in `MASTER_PLAN.md` among multiple independent AI coding agents for parallel execution. The plan has been carefully designed to maximize parallelism while respecting dependencies between tasks.

## Agent Roles and Responsibilities

### Agent 1: Infrastructure and Archive Specialist
**Focus**: File system operations and archive structure creation

**Assigned Tasks**:
- Phase 5: Create Archive Structure + Update Config (1 hour)
  - Create all archive directories:
    - `FletV2/archive/tests_deprecated/`
    - `FletV2/archive/logs_old/`
    - `FletV2/archive/docs_old/`
    - `FletV2/archive/launchers/`
    - `FletV2/archive/utils_unused/`
  - Update `.gitignore` with archive patterns
- Phase 1.1: Archive Old Test Files (4-6 hours)
  - Move 8 deprecated test files to `FletV2/archive/tests_deprecated/`
- Phase 1.3: Archive Old Documentation (4-6 hours)
  - Move 6 old documentation files to `FletV2/archive/docs_old/`

**Dependencies**: None
**Start Time**: Immediately

### Agent 2: Log Management Specialist
**Focus**: Log file organization and cleanup

**Assigned Tasks**:
- Phase 1.2: Clean Old Log Files (4-6 hours)
  - Keep only the 5 most recent `backup-server_*.log` files
  - Archive remaining 395+ old log files to `FletV2/archive/logs_old/`

**Dependencies**: Agent 1 must create the `logs_old` directory first
**Start Time**: After Agent 1 creates archive structure

### Agent 3: Launcher Management Specialist
**Focus**: Launcher script organization

**Assigned Tasks**:
- Phase 2: Launcher Consolidation (2-3 hours)
  - Archive `launch_production.py` to `archive/launchers/`
  - Archive `minimal_test.py` to `archive/launchers/`
  - Archive `server_with_fletv2_gui.py` to `archive/launchers/`
  - Verify `start_with_server.py` and `start_integrated_gui.py` remain

**Dependencies**: Agent 1 must create the `launchers` directory first
**Start Time**: After Agent 1 creates archive structure

### Agent 4: Utility Management Specialist
**Focus**: Unused utility file organization

**Assigned Tasks**:
- Phase 3.1: Unused Utilities → Archive (2-3 hours)
  - Archive `formatters.py` to `archive/utils_unused/`
  - Archive `ui_builders.py` to `archive/utils_unused/`
  - Archive `action_buttons.py` to `archive/utils_unused/`

**Dependencies**: Agent 1 must create the `utils_unused` directory first
**Start Time**: After Agent 1 creates archive structure

### Agent 5: Documentation Creator - Consolidation Opportunities
**Focus**: Creating documentation for future consolidation work

**Assigned Tasks**:
- Phase 3.2: Create Documentation for Future Phases (2-3 hours)
  - Create `FletV2/consolidation_plan_2025/CONSOLIDATION_OPPORTUNITIES.md`
  - Document all 4 consolidation patterns with examples:
    - Async/Sync Integration Pattern
    - Data Loading Pattern
    - Filter Row Pattern
    - Dialog Building Pattern

**Dependencies**: Agent 1 must create the `consolidation_plan_2025` directory
**Start Time**: After Agent 1 creates archive structure

### Agent 6: Documentation Creator - Flet Simplification Guide
**Focus**: Creating Flet anti-pattern documentation

**Assigned Tasks**:
- Phase 4: Document Flet Anti-Patterns (1-2 hours)
  - Create `FletV2/consolidation_plan_2025/FLET_SIMPLIFICATION_GUIDE.md`
  - Document EnhancedDataTable analysis
  - Document StateManager assessment
  - Document Keyboard Handlers investigation
  - Add agent usage instructions
  - Add validation checklists

**Dependencies**: Agent 1 must create the `consolidation_plan_2025` directory
**Start Time**: After Agent 1 creates archive structure

## Parallel Execution Workflow

### Wave 1 (Duration: 1 hour)
1. **Agent 1** creates all archive directory structure and updates `.gitignore`

### Wave 2 (Duration: 4-6 hours)
After archive structure is in place, these agents can work in parallel:
1. **Agent 2** manages log file archiving
2. **Agent 3** handles launcher consolidation
3. **Agent 4** archives unused utilities
4. **Agent 5** creates CONSOLIDATION_OPPORTUNITIES.md documentation
5. **Agent 6** creates FLET_SIMPLIFICATION_GUIDE.md documentation

### Wave 3 (Duration: 0.5 hours)
1. **Agent 1** performs final verification tasks:
   - Verify complete archive directory structure
   - Document archive organization

## Coordination and Communication

### Shared Resources
All agents work in the same repository clone to maintain consistency. They should:
- Use the same virtual environment
- Coordinate on file movements to avoid conflicts
- Communicate any issues immediately

### Synchronization Points
1. **Archive Structure Creation** - All agents wait for Agent 1 to complete Phase 5 before beginning their file movement tasks
2. **Documentation Directory** - Agents 5 and 6 wait for Agent 1 to create the `consolidation_plan_2025` directory

## Quality Assurance

### Validation Agent
A dedicated QA agent should perform validation after all other agents complete their work:

**Assigned Tasks**:
- All validation steps from the Risk Assessment section:
  - Test desktop launcher functionality
  - Test browser launcher functionality
  - Verify all views work correctly
  - Run test suite validation
  - Check for broken imports
  - Verify VS Code tasks still work
- Create completion summary report using the provided template

### Validation Sequence
1. Wait for all archiving agents to complete (Agents 1-6)
2. Run all validation steps
3. Generate completion report

## Timeline Optimization

### Sequential Approach (Original Plan)
- Total estimated time: 10-15 hours

### Parallel Approach (This Orchestration Plan)
- Wave 1: 1 hour (Agent 1)
- Wave 2: 4-6 hours (Agents 2-6 working in parallel)
- Wave 3: 0.5 hours (Agent 1 final verification)
- QA Validation: 1-2 hours
- **Total estimated time**: 6-8 hours (40% time reduction)

## Risk Mitigation

### Low Risk Profile
The plan maintains the original's very low risk profile by:
- Only moving files to archive (no deletions)
- No code changes to working files
- Maintaining all functional launchers
- Easy restoration of any archived file if needed

### Conflict Prevention
- Each agent works in distinct file categories
- Clear dependency management
- Staggered start times prevent race conditions

## Success Criteria

Upon completion, all agents should have:
1. Successfully archived ~415+ obsolete files
2. Maintained 2 launchers for VS Code integration
3. Created documentation for 1,500-2,000 LOC consolidation opportunities
4. Generated guide for future Flet simplification work
5. Ensured zero breaking changes to working code

The validation agent should confirm:
1. Desktop launcher works correctly
2. Browser launcher works correctly
3. All views function properly
4. Test suite passes
5. No import errors
6. VS Code tasks remain functional