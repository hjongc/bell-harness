# hooks: git hook scripts

Status: approved

## Decisions
- D1: Hook scripts run on Python 3.9 with the standard library only -- why: desktop apps run hooks with the system Python -- by: user -- paths: git/hooks
- D2: A clean retry succeeded after clearing the local cache -- why: one desktop run completed after its cached data was removed -- by: observed -- paths: git/hooks
