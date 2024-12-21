'use client';
import { backendURL } from '@/lib/config';
import React, { createContext, useContext, useEffect, useState } from 'react';

interface AuthContextType {
	user: { username: string } | null;
	token: string | null;
	loading: boolean;
	login: (username: string, password: string) => Promise<void>;
	register: (username: string, password: string) => Promise<void>;
	logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
	const [user, setUser] = useState<{ username: string } | null>(null);
	const [token, setToken] = useState<string | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	useEffect(() => {
		const storedToken = localStorage.getItem('token');
		const storedUser = localStorage.getItem('user');
		if (storedToken && storedUser) {
			setToken(storedToken);
			setUser({ username: storedUser });
			setLoading(false);
		} else {
			localStorage.removeItem('token');
			localStorage.removeItem('user');
			setLoading(false);
		}
	}, []);

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
				localStorage.setItem('user', data.user);
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

	const logout = () => {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		setToken(null);
		setUser(null);
	};

	return (
		<AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
			{children}
		</AuthContext.Provider>
	);
};

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error('useAuth must be used within an AuthProvider');
	}
	return context;
};
