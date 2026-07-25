"use client";

import { Card, CardHeader, CardBody, CardFooter } from "@/components/cards/Card";
import { Button } from "@/components/buttons/Button";
import { Input } from "@/components/inputs/Input";

export default function ProfilePage() {
  return (
    <div className="container mx-auto p-6 max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Profile</h1>
      <Card>
        <CardHeader><h2 className="text-lg font-semibold">Personal Information</h2></CardHeader>
        <CardBody className="space-y-4">
          <Input label="Name" placeholder="Your name" />
          <Input label="Email" placeholder="your@email.com" type="email" />
        </CardBody>
        <CardFooter>
          <Button variant="primary">Save Changes</Button>
        </CardFooter>
      </Card>
    </div>
  );
}