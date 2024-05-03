import React, { useEffect, useState } from "react";

const Login = () => {
    const [authUrl, setAuthUrl] = useState(''); // State to store the authentication URL

    async function initiateGoogleLogin() {
        try {
            // Fetch the response from the FastAPI endpoint
            const response = await fetch('http://localhost:8000/auth/google/login');
            const data = await response.json();

            // Assuming the authentication URL is stored in a global variable or can be retrieved from the server
            // For this example, replace the URL with your actual Google authentication URL
            const authenticationUrl = data.message;

            // Set the authentication URL in the state
            setAuthUrl(authenticationUrl);

            // Open a new window or tab with the authentication URL
            window.open(authenticationUrl, '_blank');
        } catch (error) {
            console.error('Error initiating Google login:', error);
        }
    }

    useEffect(() => {
        document.getElementById('loginButton').addEventListener('click', initiateGoogleLogin);
        return () => {
            document.getElementById('loginButton').removeEventListener('click', initiateGoogleLogin);
        };
    }, []);

    return (
        <div>
            <h1>Log In</h1>
            <button id="loginButton">Sign in with Google</button>
            {/* Display the authentication URL */}
            {authUrl && <p>Authentication URL: {authUrl}</p>}
        </div>
    );
};

export default Login;