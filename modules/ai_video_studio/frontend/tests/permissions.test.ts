import { describe, expect, it } from 'vitest';
import { hasPermission, roleLabel } from '../src/permissions';
import type { Role, User } from '../src/types';

function user(role: Role): User {
  return { id: 'u1', name: 'Test', email: 'test@example.com', role, status: 'active' };
}

describe('hasPermission', () => {
  it('denies everything for null users', () => {
    expect(hasPermission(null, 'project:read')).toBe(false);
    expect(hasPermission(null, '*')).toBe(false);
  });

  it('grants everything to the owner', () => {
    expect(hasPermission(user('owner'), 'project:read')).toBe(true);
    expect(hasPermission(user('owner'), 'team:manage')).toBe(true);
    expect(hasPermission(user('owner'), 'anything:at:all')).toBe(true);
  });

  it('grants admin-scoped permissions to admins', () => {
    expect(hasPermission(user('admin'), 'project:write')).toBe(true);
    expect(hasPermission(user('admin'), 'settings:manage')).toBe(true);
    expect(hasPermission(user('admin'), 'team:manage')).toBe(true);
  });

  it('denies admin-only permissions to editors', () => {
    expect(hasPermission(user('editor'), 'project:write')).toBe(true);
    expect(hasPermission(user('editor'), 'team:manage')).toBe(false);
    expect(hasPermission(user('editor'), 'settings:manage')).toBe(false);
  });

  it('grants read-only access to viewers', () => {
    expect(hasPermission(user('viewer'), 'project:read')).toBe(true);
    expect(hasPermission(user('viewer'), 'analytics:read')).toBe(true);
    expect(hasPermission(user('viewer'), 'project:write')).toBe(false);
  });
});

describe('roleLabel', () => {
  it('capitalizes role names', () => {
    expect(roleLabel('owner')).toBe('Owner');
    expect(roleLabel('admin')).toBe('Admin');
    expect(roleLabel('editor')).toBe('Editor');
    expect(roleLabel('viewer')).toBe('Viewer');
  });
});
