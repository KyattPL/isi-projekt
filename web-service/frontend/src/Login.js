import React, { useState } from "react";
import { Button, Typography } from "@mui/material";

const Login = () => {
    // const [authUrl, setAuthUrl] = useState('');

    async function initiateGoogleLogin() {
        try {
            const response = await fetch('http://localhost:8000/auth/google/login');
            const data = await response.json();
            const authenticationUrl = data.message;
            // setAuthUrl(authenticationUrl);
            window.open(authenticationUrl, '_blank');
        } catch (error) {
            console.error('Error initiating Google login:', error);
        }
    }

    // useEffect(() => {
    //     document.getElementById('loginButton').addEventListener('click', initiateGoogleLogin);
    //     return () => {
    //         document.getElementById('loginButton').removeEventListener('click', initiateGoogleLogin);
    //     };
    // }, []);

    return (
        <div>
            <Typography>Log in</Typography>
            <Button onClick={initiateGoogleLogin}>Sign in with Google</Button>
        </div>
    );
};

export default Login;