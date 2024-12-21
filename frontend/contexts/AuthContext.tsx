'use client';
import { backendURL } from '@/lib/config';
import React, { createContext, useContext, useEffect, useState } from 'react';

interface AuthContextType {
	user: { username: string } | null; // The user's information or null if not authenticated
	token: string | null;
	loading: boolean;
	login: (username: string, password: string) => Promise<void>; // Log in function
	register: (username: string, password: string) => Promise<void>; // Register function
	logout: () => void; // Log out function
}
// Create the AuthContext
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider component to wrap the application
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
	const [user, setUser] = useState<{ username: string } | null>(null); // Store the authenticated user's info
	const [token, setToken] = useState<string | null>(''); // Store the JWT token
	const [loading, setloading] = useState<boolean>(false);

	useEffect(() => {
		setloading(true);
		// Fetch token from localStorage on component mount
		const storedToken = localStorage.getItem('token');
		if (storedToken) {
			setToken(storedToken);
			// fetchUser(storedToken);
		}
		setloading(false);
	}, []);

	// // Fetch user information from the backend using the token
	// const fetchUser = async (token) => {
	// 	try {
	// 		const response = await fetch('/api/me', {
	// 			headers: { Authorization: `Bearer ${token}` },
	// 		});
	// 		if (response.ok) {
	// 			const data = await response.json();
	// 			setUser(data.user);
	// 		} else {
	// 			logout(); // Clear token if fetching user fails
	// 		}
	// 	} catch (error) {
	// 		console.error('Error fetching user:', error);
	// 		logout();
	// 	}
	// };

	// Register a new user
	const register = async (username: string, password: string): Promise<void> => {
		try {
			const response = await fetch(`${backendURL}/register`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password }),
			});
			const data = await response.json();
			if (data.success) {
				alert('Registration successful. You can now log in.');
			} else {
				alert(data.message || 'Registration failed');
			}
		} catch (error) {
			console.error('Registration error:', error);
		}
	};

	// Log in a user
	const login = async (username: string, password: string): Promise<void> => {
		try {
			const response = await fetch(`${backendURL}/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password }),
			});
			const data = await response.json();
			if (data.success) {
				localStorage.setItem('token', data.token);
				setToken(data.token);
				setUser({ username: data.user });
				alert('Login successful');
			} else {
				alert(data.message || 'Login failed');
			}
		} catch (error) {
			console.error('Login error:', error);
		}
	};

	// Log out the user
	const logout = () => {
		localStorage.removeItem('token');
		setToken(null);
		setUser(null);
	};

	return (
		<AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
			{children}
		</AuthContext.Provider>
	);
};

// useAuth hook for consuming the AuthContext
export const useAuth = () => {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error('UseAuth must be used within an AuthProvider');
	}
	return context;
};
