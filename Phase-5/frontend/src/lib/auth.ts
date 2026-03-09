import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

// Initialize Better Auth client with JWT plugin for FastAPI compatibility
export const authClient = createAuthClient({
  basePath: "/api/auth", // Better Auth runs inside Next.js, not FastAPI
  plugins: [
    jwtClient() // Enable JWT client to get JWT tokens for FastAPI
  ],
});

// Enhanced session retrieval with debugging
export async function getSessionWithDebug() {
  try {
    const session = await authClient.getSession();

    // Also try to get the JWT token separately
    const tokenResponse = await authClient.token();
    const token = tokenResponse?.data?.token;

    // Log for debugging purposes
    console.log("Better Auth session received:", {
      hasSession: !!session,
      hasSessionData: !!session?.data?.session,
      hasToken: !!token,
      tokenPresent: !!token,
      tokenResponse: tokenResponse,
      sessionKeys: session?.data ? Object.keys(session.data) : 'no session',
      sessionStructure: JSON.stringify(session, null, 2)
    });

    return session;
  } catch (error) {
    console.error("Error getting Better Auth session:", error);
    throw error;
  }
}

// Export a function to get the JWT token directly
export async function getJwtToken() {
  try {
    const tokenResponse = await authClient.token();
    return tokenResponse?.data?.token || null;
  } catch (error) {
    console.error("Error getting JWT token:", error);
    return null;
  }
}

// Export individual client methods
export const { signIn, signOut, signUp, getSession } = authClient;
