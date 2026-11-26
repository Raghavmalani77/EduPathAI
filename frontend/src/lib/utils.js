import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges Tailwind CSS class names safely.
 * Drop-in equivalent of shadcn/ui's cn() utility.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
