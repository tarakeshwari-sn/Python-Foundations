# Project Management Tool

To keep track of the development of a project and its progress.

Purpose:
* Plan work
* Track tasks/issues
* Assign responsibility
* Control workflow
* Enforce role-based access

## Roles and operations: 
### Admin

1. create_project()
2. delete_project()
3. define_workflow()
4. create_user()
5. assign_role()
6. deactivate_user()

### Project Manager

1. create_issue()
2. assign_issue()
3. update_priority()
4. change_status()
5. generate_report()

### User

1. report_issue()
2. add_comment()
3. update_status()
4. view_assigned_issues()

## Classes and attributes: 

1. Account :
    * user_id
    * name
    * email
    * role
    * is_active

2. Admin (extends Account): 
    * permissions

3. ProjectManager (extends Account): 
    * managed_projects

4. User (extends Account): 
    * assigned_issues

5. Project: 
    * project_id
    * name
    * key
    * members
    * issues

6. Issue: 
    * issue_id
    * title
    * description
    * issue_type
    * status
    * priority
    * reporter
    * assignee
    * project
    * created_at
    * updated_at

7. Comment: 
    * comment_id
    * issue
    * author
    * content
    * created_at

8. Workflow: 
    * workflow_id
    * allowed_transitions

9. PermissionManager: 
    * role_permissions

10. AuditLog: 
    * log_id
    * actor (person working on the issue)
    * action
    * target
    * timestamp