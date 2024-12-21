import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export const Login: React.FC = () => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const { login } = useAuth();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		try {
			// Use the login function from the context
			await login(username, password);
			// alert('Login successful');
		} catch (error) {
			console.error('Login error:', error);
			// alert('Login failed');
		}
	};

	return (
		<Card className="w-full max-w-md">
			<form onSubmit={handleSubmit}>
				<CardHeader>
					<CardTitle>Login</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="space-y-4">
						<Input
							type="text"
							placeholder="Username"
							value={username}
							onChange={(e) => setUsername(e.target.value)}
							required
						/>
						<Input
							type="password"
							placeholder="Password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
						/>
					</div>
				</CardContent>
				<CardFooter>
					<Button type="submit" onClick={handleSubmit}>
						Login
					</Button>
				</CardFooter>
			</form>
		</Card>
	);
};
