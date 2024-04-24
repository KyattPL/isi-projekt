import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function Home() {
    const [inputValue, setInputValue] = useState('');
    const navigate = useNavigate();

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
    };

    const handleSearch = async () => {
        // console.log("here");
        // let [gameName, tagLine] = inputValue.split("#");
        // const response = await fetch(`http://localhost:8000/matches_data_by_riot_id/${gameName}/${tagLine}`);
        // console.log("here 2");
        // const data = await response.json();
        // console.log(data);

        let [gameName, tagLine] = inputValue.split("#");
        navigate(`/search-results/${gameName}/${tagLine}`);
    };

    return (
        <Container>
            <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                height="100vh"
            >
                <Typography variant="h4" component="h1" gutterBottom>
                    Welcome to Clone.gg
                </Typography>
                <TextField
                    label="Search"
                    variant="outlined"
                    size="small"
                    value={inputValue}
                    onChange={handleInputChange}
                    sx={{ marginBottom: 2 }}
                />
                <Button variant="contained" color="primary" onClick={handleSearch}>
                    Search
                </Button>
            </Box>
        </Container>
    );
}

export default Home;
