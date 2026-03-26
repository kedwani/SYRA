/**
 * Home Page
 * Landing page demonstrating the SYRA component library
 */

'use client';

import { Button, Input, Card, CardHeader, CardBody, SkipLink, SkipLinkTarget } from '@/components';
import { useState } from 'react';

export default function Home() {
  const [formData, setFormData] = useState({ email: '', password: '' });

  return (
    <>
      {/* Skip Link for keyboard accessibility - WCAG 2.4.1 */}
      <SkipLink targetId="main-content">Skip to main content</SkipLink>
      
      <main 
        id="main-content"
        className="min-h-screen flex flex-col items-center justify-center p-8 bg-gray-50"
      >
        <div className="max-w-md w-full text-center space-y-6">
          {/* Page Title */}
          <h1 className="text-4xl font-bold text-gray-900">
            Welcome to SYRA
          </h1>
          <p className="text-lg text-gray-600">
            Medical Emergency Identification System
          </p>
          
          {/* Card demonstrating component usage */}
          <Card variant="medical">
            <CardHeader 
              title="Your Medical Profile" 
              subtitle="Access your emergency medical information"
            />
            <CardBody>
              <p className="text-gray-500">
                Your medical profile dashboard will appear here.
              </p>
            </CardBody>
          </Card>
          
          {/* Login Form with accessible Input components */}
          <Card>
            <CardBody>
              <form className="space-y-4">
                <Input
                  label="Email Address"
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
                <Input
                  label="Password"
                  type="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
                <Button 
                  type="submit" 
                  variant="primary" 
                  className="w-full"
                >
                  Sign In
                </Button>
              </form>
            </CardBody>
          </Card>
          
          {/* Action Buttons demonstrating variants */}
          <div className="flex gap-4 justify-center flex-wrap">
            <Button variant="primary">
              Login
            </Button>
            <Button variant="outline">
              Register
            </Button>
            <Button variant="ghost">
              Learn More
            </Button>
          </div>
          
          {/* Skip Link Target - where keyboard users will land */}
          <SkipLinkTarget id="main-content" />
        </div>
      </main>
    </>
  );
}
