import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';

export const Register: React.FC<{ onRegister: () => void }> = () => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const { register } = useAuth();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		try {
			await register(username, password);
			// alert('Registration successful. Please login.');
		} catch (error) {
			console.error('Registration error:', error);
			// alert('Registration failed');
		}
	};

	return (
		<Card className="w-full max-w-md">
			<CardHeader>
				<CardTitle>Register</CardTitle>
			</CardHeader>
			<CardContent>
				<form onSubmit={handleSubmit}>
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
				</form>
			</CardContent>
			<CardFooter>
				<Button type="submit" onClick={handleSubmit}>
					Register
				</Button>
			</CardFooter>
		</Card>
	);
};
