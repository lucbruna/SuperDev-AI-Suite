"use client";

import { Card, CardHeader, CardBody } from "@/components/cards/Card";
import { Table } from "@/components/tables/Table";

interface UserRow {
  id: string;
  name: string;
  email: string;
  role: string;
}

const mockUsers: UserRow[] = [
  { id: "1", name: "Admin User", email: "admin@superdev.ai", role: "admin" },
  { id: "2", name: "Developer", email: "dev@superdev.ai", role: "developer" },
];

export default function AdminUsersPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">User Management</h1>
      <Card>
        <CardHeader><h2 className="text-lg font-semibold">All Users</h2></CardHeader>
        <CardBody>
          <Table
            columns={[
              { key: "name", header: "Name", render: (u: UserRow) => u.name },
              { key: "email", header: "Email", render: (u: UserRow) => u.email },
              { key: "role", header: "Role", render: (u: UserRow) => u.role },
            ]}
            data={mockUsers}
            keyExtractor={(u: UserRow) => u.id}
          />
        </CardBody>
      </Card>
    </div>
  );
}