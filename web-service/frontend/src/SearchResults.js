import React from 'react';
import { Container, Typography } from '@mui/material';
import { useLocation } from 'react-router-dom';

function SearchResults() {
    const location = useLocation();
    const searchResults = location.state?.data;

    return (
        <Container>
            <Typography variant="h4" component="h1" gutterBottom>
                Search Results
            </Typography>
            {searchResults}
        </Container>
    );
}

export default SearchResults;