import React from 'react';
import { Container, Typography, TextField, Button } from '@mui/material';

function Login() {
    return (
        <Container>
            <Typography variant="h4" component="h1" gutterBottom>
                Log In
            </Typography>
            <TextField />
            <Button />
        </Container>
    );
}

export default Login;