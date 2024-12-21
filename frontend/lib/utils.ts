import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


// export const fetchOptions = {
//   credentials: 'include' as const,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// };