import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
	baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
	secret: process.env.BETTER_AUTH_SECRET,
	trustedOrigins: [
		"http://localhost:3000",
		"http://192.168.49.2:30300",
		process.env.BETTER_AUTH_URL || "http://localhost:3000",
	].filter(Boolean),
	database: new Pool({
		connectionString: process.env.DATABASE_URL,
	}),
	emailAndPassword: {
		enabled: true,
	},
	plugins: [
		nextCookies(), // For Next.js cookie handling
		jwt() // Add JWT plugin to generate JWT tokens
	],
});