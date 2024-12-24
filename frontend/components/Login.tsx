import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import LoadingSpinner from './loading-spinner';

export const Login: React.FC = () => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [isLoading, setIsLoading] = useState(false); // Loading state
	const { login } = useAuth();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true); // Start loading
		try {
			// Use the login function from the context
			await login(username, password);
			// Optionally handle post-login logic here
		} catch (error) {
			console.error('Login error:', error);
		} finally {
			setIsLoading(false); // Stop loading
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
							disabled={isLoading} // Disable input while loading
						/>
						<Input
							type="password"
							placeholder="Password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							required
							disabled={isLoading} // Disable input while loading
						/>
					</div>
				</CardContent>
				<CardFooter className="flex items-center justify-between">
					<Button type="submit" disabled={isLoading}>
						{isLoading ? <LoadingSpinner /> : 'Login'}
					</Button>
				</CardFooter>
			</form>
		</Card>
	);
};
