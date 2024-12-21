'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Login } from '@/components/Login';
import { Register } from '@/components/Register';
import { useAuth } from '@/contexts/AuthContext';
import { backendURL } from '@/lib/config';

interface Message {
	id: number;
	text: string;
	sender: 'user' | 'bot';
	timestamp: string;
}

interface Product {
	id: number;
	name: string;
	category: string;
	price: number;
	description: string;
	stock: number;
}

export default function Home() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState('');
	const [products, setProducts] = useState<Product[]>([]);
	const [category, setCategory] = useState<string>('');
	const [priceRange, setPriceRange] = useState<number[]>([0, 1000]);
	const [showRegister, setShowRegister] = useState(false);
	const scrollAreaRef = useRef<HTMLDivElement>(null);
	const { user, logout } = useAuth();

	useEffect(() => {
		if (user) {
			setMessages([
				{
					id: 0,
					text: `Welcome back, ${user}! How can I assist you today?`,
					sender: 'bot',
					timestamp: new Date().toISOString(),
				},
			]);
			fetchChatHistory();
		}
	}, [user]);

	useEffect(() => {
		if (scrollAreaRef.current) {
			scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
		}
	}, [messages]);

	const fetchChatHistory = async () => {
		try {
			const response = await fetch(`${backendURL}/chat_history`, {
				credentials: 'include',
			});
			const data = await response.json();
			if (Array.isArray(data)) {
				setMessages(
					data.map((msg: any, index: number) => ({
						id: index,
						text: msg.message,
						sender: msg.sender,
						timestamp: new Date(msg.timestamp).toISOString(),
					}))
				);
			} else {
				console.error('Unexpected chat history data format:', data);
			}
		} catch (error) {
			console.error('Error fetching chat history:', error);
		}
	};

	const saveChat = async (message: string, sender: 'user' | 'bot') => {
		try {
			await fetch(`${backendURL}/save_chat`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ message, sender }),
				credentials: 'include',
			});
		} catch (error) {
			console.error('Error saving chat message:', error);
		}
	};

	const handleSendMessage = async () => {
		if (input.trim() === '') return;

		const userMessage: Message = {
			id: messages.length,
			text: input,
			sender: 'user',
			timestamp: new Date().toISOString(),
		};

		setMessages((prevMessages) => [...prevMessages, userMessage]);
		saveChat(input, 'user');
		setInput('');

		try {
			const response = await fetch(
				`${backendURL}/search?q=${encodeURIComponent(
					input
				)}&category=${category}&min_price=${priceRange[0]}&max_price=${priceRange[1]}`,
				{
					credentials: 'include',
				}
			);
			const data = await response.json();
			if (Array.isArray(data)) {
				setProducts(data);
				const botResponse: Message = {
					id: messages.length + 1,
					text: `I found ${data.length} products matching your query. Here are the results:`,
					sender: 'bot',
					timestamp: new Date().toISOString(),
				};
				setMessages((prevMessages) => [...prevMessages, botResponse]);
				saveChat(botResponse.text, 'bot');
			} else {
				throw new Error('Unexpected data format from search');
			}
		} catch (error) {
			console.error('Error fetching products:', error);
			const errorMessage: Message = {
				id: messages.length + 1,
				text: 'Sorry, I encountered an error while searching for products. Please try again later.',
				sender: 'bot',
				timestamp: new Date().toISOString(),
			};
			setMessages((prevMessages) => [...prevMessages, errorMessage]);
			saveChat(errorMessage.text, 'bot');
		}
	};

	const handlePurchase = async (productId: number) => {
		try {
			const response = await fetch(`${backendURL}/purchase`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ product_id: productId }),
				credentials: 'include',
			});
			const data = await response.json();
			if (data.success) {
				const purchaseMessage: Message = {
					id: messages.length + 1,
					text: data.message,
					sender: 'bot',
					timestamp: new Date().toISOString(),
				};
				setMessages((prevMessages) => [...prevMessages, purchaseMessage]);
				saveChat(purchaseMessage.text, 'bot');
				setProducts((prevProducts) =>
					prevProducts.map((product) =>
						product.id === productId
							? { ...product, stock: product.stock - 1 }
							: product
					)
				);
			} else {
				throw new Error(data.message);
			}
		} catch (error) {
			console.error('Error purchasing product:', error);
			const errorMessage: Message = {
				id: messages.length + 1,
				text: 'Sorry, I encountered an error while processing your purchase. Please try again later.',
				sender: 'bot',
				timestamp: new Date().toISOString(),
			};
			setMessages((prevMessages) => [...prevMessages, errorMessage]);
			saveChat(errorMessage.text, 'bot');
		}
	};

	const handleReset = () => {
		setMessages([
			{
				id: 0,
				text: `Welcome back, ${user}! How can I assist you today?`,
				sender: 'bot',
				timestamp: new Date().toISOString(),
			},
		]);
		setProducts([]);
		setCategory('');
		setPriceRange([0, 1000]);
	};

	const handleLogout = async () => {
		try {
			await fetch(`${backendURL}/logout`, {
				method: 'POST',
				credentials: 'include',
			});
			logout();
			setMessages([]);
			setProducts([]);
			setCategory('');
			setPriceRange([0, 1000]);
		} catch (error) {
			console.error('Error logging out:', error);
		}
	};

	if (!user) {
		return (
			<main className="flex min-h-screen flex-col items-center justify-center p-24">
				{showRegister ? (
					<Register onRegister={() => setShowRegister(false)} />
				) : (
					<>
						<Login />
						<Button onClick={() => setShowRegister(true)} className="mt-4">
							Register
						</Button>
					</>
				)}
			</main>
		);
	}

	return (
		<main className="flex min-h-screen flex-col items-center justify-between p-4 sm:p-8 md:p-24">
			<Card className="w-full max-w-4xl">
				<CardHeader className="flex flex-row items-center justify-between">
					<CardTitle>E-Commerce Chatbot</CardTitle>
					<Button onClick={handleLogout}>Logout</Button>
				</CardHeader>
				<CardContent>
					<ScrollArea
						className="h-[400px] w-full rounded-md border p-4"
						ref={scrollAreaRef}
					>
						{messages.map((message) => (
							<div
								key={message.id}
								className={`mb-4 ${
									message.sender === 'user' ? 'text-right' : 'text-left'
								}`}
							>
								<div
									className={`inline-block rounded-lg p-2 ${
										message.sender === 'user'
											? 'bg-primary text-primary-foreground'
											: 'bg-muted'
									}`}
								>
									{message.text}
								</div>
								<div className="text-xs text-muted-foreground mt-1">
									{new Date(message.timestamp).toLocaleTimeString()}
								</div>
							</div>
						))}
					</ScrollArea>
					<div className="mt-4 space-y-4">
						<div className="flex space-x-2">
							<Select value={category} onValueChange={setCategory}>
								<SelectTrigger className="w-[180px]">
									<SelectValue placeholder="Select category" />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="all">All Categories</SelectItem>
									<SelectItem value="Electronics">Electronics</SelectItem>
									<SelectItem value="Books">Books</SelectItem>
									<SelectItem value="Clothing">Clothing</SelectItem>
									<SelectItem value="Home & Garden">Home & Garden</SelectItem>
									<SelectItem value="Toys">Toys</SelectItem>
								</SelectContent>
							</Select>
							<div className="flex-1">
								<Slider
									min={0}
									max={1000}
									step={10}
									value={priceRange}
									onValueChange={setPriceRange}
								/>
								<div className="flex justify-between mt-2">
									<span>${priceRange[0]}</span>
									<span>${priceRange[1]}</span>
								</div>
							</div>
						</div>
					</div>
					{products.length > 0 && (
						<div className="mt-4 overflow-x-auto">
							<h3 className="text-lg font-semibold mb-2">Product Results:</h3>
							<div className="flex space-x-4">
								{products.map((product) => (
									<div
										key={product.id}
										className="border rounded p-2 min-w-[200px]"
									>
										<h4 className="font-semibold">{product.name}</h4>
										<p>Price: ${product.price.toFixed(2)}</p>
										<p>Category: {product.category}</p>
										<p>Stock: {product.stock}</p>
										<p className="text-sm text-muted-foreground">
											{product.description}
										</p>
										<Button
											onClick={() => handlePurchase(product.id)}
											disabled={product.stock === 0}
											className="mt-2"
										>
											{product.stock > 0 ? 'Purchase' : 'Out of Stock'}
										</Button>
									</div>
								))}
							</div>
						</div>
					)}
				</CardContent>
				<CardFooter className="flex justify-between">
					<div className="flex-grow mr-2">
						<Input
							type="text"
							placeholder="Type your message..."
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
						/>
					</div>
					<Button onClick={handleSendMessage}>Send</Button>
					<Button variant="outline" onClick={handleReset} className="ml-2">
						Reset
					</Button>
				</CardFooter>
			</Card>
		</main>
	);
}
