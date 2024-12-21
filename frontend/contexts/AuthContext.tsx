'use client';
import React, { createContext, useState, useContext, useEffect } from 'react';

interface AuthContextType {
	user: string | null;
	login: (username: string) => void;
	logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [user, setUser] = useState<string | null>(null);

	useEffect(() => {
		// Check for stored user on component mount
		const storedUser = localStorage.getItem('user');
		if (storedUser) {
			setUser(storedUser);
		}
	}, []);

	const login = (username: string) => {
		setUser(username);
		localStorage.setItem('user', username);
	};

	const logout = () => {
		setUser(null);
		localStorage.removeItem('user');
	};

	return <AuthContext.Provider value={{ user, login, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error('useAuth must be used within an AuthProvider');
	}
	return context;
};
