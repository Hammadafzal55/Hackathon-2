# ADR: Authentication Architecture with Existing User Table Integration

## Status
Proposed

## Date
2026-01-16

## Context
The Todo application already has an existing user table structure in the backend using SQLModel and Neon PostgreSQL. Better Auth typically creates its own user tables, but we need to integrate with the existing user table to maintain consistency and avoid duplicating user data.

## Decision
We will configure Better Auth to work with the existing user table by:
1. Using Better Auth's custom schema configuration to map field names
2. Updating the existing user model to be compatible with Better Auth requirements
3. Adding any additional fields needed for Better Auth functionality
4. Maintaining the existing user table structure while allowing Better Auth to manage authentication

## Alternatives Considered
1. **Create separate Better Auth tables**: Would result in duplicate user data and complex synchronization
2. **Migrate existing users to Better Auth tables**: Would require complex data migration and risk data loss
3. **Maintain both user systems**: Would create security and maintenance issues

## Consequences
### Positive
- Maintains existing user data integrity
- Preserves existing application logic that depends on user structure
- Leverages Better Auth's authentication capabilities
- Reduces data duplication

### Negative
- Requires careful field mapping between systems
- May need additional compatibility layers
- Could be more complex to configure initially

## Technical Approach
- Use Better Auth's `user.modelName` and `user.fields` configuration options to map to existing table
- Add any required additional fields to the existing user model
- Configure JWT token generation to include existing user ID
- Update authentication middleware to work with existing user structure