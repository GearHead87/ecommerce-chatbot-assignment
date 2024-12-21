export interface MessageType {
	message: string;
	sender: 'user' | 'bot';
	timestamp: string | number;
}
