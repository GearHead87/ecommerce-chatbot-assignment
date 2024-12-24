import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from './loading-spinner';

export const Register: React.FC<{ onRegister: () => void }> = ({ onRegister }) => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [isLoading, setIsLoading] = useState(false); // Loading state
	const { register } = useAuth();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true); // Start loading
		try {
			await register(username, password);
			onRegister(); // Notify parent component after successful registration
		} catch (error) {
			console.error('Registration error:', error);
		} finally {
			setIsLoading(false); // Stop loading
		}
	};

	return (
		<Card className="w-full max-w-md">
			<form onSubmit={handleSubmit}>
				<CardHeader>
					<CardTitle>Register</CardTitle>
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
				<CardFooter>
					<Button type="submit" disabled={isLoading}>
						{isLoading ? <LoadingSpinner /> : 'Register'}
					</Button>
				</CardFooter>
			</form>
		</Card>
	);
};
