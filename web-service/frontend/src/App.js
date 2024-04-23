import React from 'react';
import { Container, Typography, TextField, Button } from '@mui/material';

function App() {
  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        Clone.gg
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        label="Search"
        placeholder="Provide your Riot ID"
      />
      <Button variant="contained" color="primary" style={{ marginTop: '16px' }}>
        Search
      </Button>
    </Container>
  );
}

export default App;